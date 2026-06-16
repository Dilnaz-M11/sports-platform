import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(null);
  const [step, setStep] = useState('login');
  const [weeks, setWeeks] = useState({});
  const [currentWeek, setCurrentWeek] = useState(1);
  const [loading, setLoading] = useState(false);

  const [userData, setUserData] = useState({
    birth_date: '',
    gender: 'male',
    weight_kg: '',
    height_cm: '',
    fitness_level: 'beginner',
    rest_hr: '',
    max_hr: ''
  });

  const [goalData, setGoalData] = useState({
    goal_type: 'weight_loss',
    target_value: '',
    deadline_weeks: 8
  });

  // ✅ URL для продакшена на Render
  const api = axios.create({ 
    baseURL: 'https://sports-platform-api-b9e4.onrender.com' 
  });

  // Перехватчик для добавления токена
  api.interceptors.request.use((config) => {
    const currentToken = localStorage.getItem('token');
    if (currentToken) {
      config.headers.Authorization = `Bearer ${currentToken}`;
    }
    return config;
  });

  // Функция выхода
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsLoggedIn(false);
    setStep('login');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData(e.target);
    try {
      const response = await api.post('/api/auth/login', {
        username: formData.get('username'),
        password: formData.get('password')
      }, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
      const newToken = response.data.access_token;
      setToken(newToken);
      localStorage.setItem('token', newToken);
      api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      setIsLoggedIn(true);
      setStep('profile');
    } catch (error) {
      alert('❌ Ошибка входа. Проверьте логин и пароль.');
    }
    setLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    const formData = new FormData(e.target);
    try {
      await api.post('/api/auth/register', {
        login: formData.get('login'),
        email: formData.get('email'),
        password: formData.get('password'),
        birth_date: formData.get('birth_date'),
        gender: formData.get('gender'),
        weight_kg: parseFloat(formData.get('weight_kg')),
        height_cm: parseFloat(formData.get('height_cm')),
        fitness_level: formData.get('fitness_level')
      });
      alert('✅ Регистрация успешна! Теперь войдите в систему.');
    } catch (error) {
      alert('❌ Ошибка регистрации. Возможно, такой пользователь уже существует.');
    }
    setLoading(false);
  };

  const updateProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/api/plan/update-profile', userData);
      setStep('goal');
    } catch (error) {
      alert('❌ Ошибка сохранения профиля');
    }
    setLoading(false);
  };

  // ✅ ИСПРАВЛЕНО: улучшенная обработка токенов и ошибок
  const createGoal = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      let targetValue = goalData.target_value;
      
      // Для "общего оздоровления" всегда передаем 0
      if (goalData.goal_type === 'health') {
        targetValue = 0;
      }
      
      // Преобразуем в число и проверяем
      const numericTarget = parseFloat(targetValue);
      if (isNaN(numericTarget) && goalData.goal_type !== 'health') {
        alert('⚠️ Пожалуйста, укажите корректное целевое значение');
        setLoading(false);
        return;
      }
      
      const payload = {
        goal_type: goalData.goal_type,
        target_value: goalData.goal_type === 'health' ? 0 : numericTarget,
        deadline_weeks: goalData.deadline_weeks
      };
      
      // Создаем цель
      const response = await api.post('/api/plan/create-goal', payload);
      console.log('✅ Цель создана:', response.data);
      
      // ✅ ПРОВЕРЯЕМ ТОКЕН ПЕРЕД ГЕНЕРАЦИЕЙ
      const currentToken = localStorage.getItem('token');
      if (!currentToken) {
        alert('❌ Сессия истекла. Пожалуйста, войдите заново.');
        handleLogout();
        setLoading(false);
        return;
      }
      
      // ✅ ЯВНО УСТАНАВЛИВАЕМ ТОКЕН ДЛЯ ЗАПРОСА
      api.defaults.headers.common['Authorization'] = `Bearer ${currentToken}`;
      
      // Генерируем план
      setStep('plan');
      const generateResponse = await api.post('/api/plan/generate');
      
      // Формируем структуру недель
      const weeksMap = {};
      generateResponse.data.plan.forEach(item => {
        if (!weeksMap[item.week]) weeksMap[item.week] = [];
        weeksMap[item.week].push(item);
      });
      setWeeks(weeksMap);
      
    } catch (error) {
      console.error('❌ Ошибка создания цели:', error);
      if (error.response && error.response.status === 401) {
        alert('❌ Сессия истекла. Пожалуйста, войдите заново.');
        handleLogout();
      } else if (error.response) {
        alert(`❌ Ошибка: ${error.response.data.detail || error.response.statusText}`);
      } else if (error.request) {
        // Запрос не дошел до сервера (CORS или сеть)
        alert('❌ Ошибка сети. Проверьте подключение к интернету.');
      } else {
        alert('❌ Ошибка создания цели. Проверьте консоль для деталей.');
      }
    }
    setLoading(false);
  };

  // Загрузка сохраненного плана при входе
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) { 
      setToken(savedToken); 
      setIsLoggedIn(true); 
      setStep('profile');
      api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
      api.get('/api/plan/current').then(res => {
        if (res.data.weeks && Object.keys(res.data.weeks).length > 0) {
          setWeeks(res.data.weeks);
          setStep('plan');
        }
      }).catch(() => {});
    }
  }, []);

  // Стили для светлой темы
  const styles = {
    container: {
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    },
    card: {
      background: 'white',
      borderRadius: '20px',
      boxShadow: '0 20px 60px rgba(0,0,0,0.1)',
      padding: '40px',
      maxWidth: '520px',
      margin: '0 auto',
      transition: 'all 0.3s ease'
    },
    cardWide: {
      background: 'white',
      borderRadius: '20px',
      boxShadow: '0 20px 60px rgba(0,0,0,0.1)',
      padding: '40px',
      maxWidth: '1200px',
      margin: '0 auto'
    },
    input: {
      width: '100%',
      padding: '12px 16px',
      marginBottom: '16px',
      border: '2px solid #e2e8f0',
      borderRadius: '12px',
      fontSize: '16px',
      transition: 'border-color 0.3s ease',
      boxSizing: 'border-box',
      background: '#f7fafc'
    },
    select: {
      width: '100%',
      padding: '12px 16px',
      marginBottom: '16px',
      border: '2px solid #e2e8f0',
      borderRadius: '12px',
      fontSize: '16px',
      background: '#f7fafc',
      boxSizing: 'border-box'
    },
    buttonPrimary: {
      width: '100%',
      padding: '14px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      fontSize: '18px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'transform 0.2s ease, box-shadow 0.2s ease',
      boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)'
    },
    buttonSecondary: {
      padding: '10px 24px',
      background: 'white',
      color: '#4a5568',
      border: '2px solid #e2e8f0',
      borderRadius: '10px',
      fontSize: '15px',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.2s ease'
    },
    buttonBack: {
      padding: '10px 20px',
      background: 'white',
      color: '#4a5568',
      border: '2px solid #e2e8f0',
      borderRadius: '10px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      display: 'flex',
      alignItems: 'center',
      gap: '8px'
    },
    buttonDanger: {
      padding: '8px 20px',
      background: 'linear-gradient(135deg, #fc8181 0%, #e53e3e 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '10px',
      fontSize: '14px',
      cursor: 'pointer',
      boxShadow: '0 4px 15px rgba(229, 62, 62, 0.3)'
    },
    label: {
      display: 'block',
      fontSize: '14px',
      fontWeight: '600',
      color: '#4a5568',
      marginBottom: '6px'
    },
    title: {
      fontSize: '28px',
      fontWeight: '700',
      color: '#2d3748',
      marginBottom: '8px',
      textAlign: 'center'
    },
    subtitle: {
      fontSize: '16px',
      color: '#718096',
      textAlign: 'center',
      marginBottom: '24px'
    },
    header: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '20px 0',
      borderBottom: '2px solid #e2e8f0',
      marginBottom: '30px'
    },
    logo: {
      fontSize: '24px',
      fontWeight: '700',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent'
    },
    table: {
      width: '100%',
      borderCollapse: 'collapse',
      background: 'white',
      borderRadius: '12px',
      overflow: 'hidden',
      boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
    },
    th: {
      background: '#f7fafc',
      padding: '12px 16px',
      textAlign: 'left',
      fontSize: '14px',
      fontWeight: '600',
      color: '#4a5568',
      borderBottom: '2px solid #e2e8f0'
    },
    td: {
      padding: '12px 16px',
      borderBottom: '1px solid #e2e8f0',
      fontSize: '14px',
      color: '#2d3748'
    },
    badge: {
      display: 'inline-block',
      padding: '4px 12px',
      borderRadius: '20px',
      fontSize: '12px',
      fontWeight: '600'
    },
    badgeSuccess: {
      background: '#c6f6d5',
      color: '#22543d'
    },
    badgeWarning: {
      background: '#fefcbf',
      color: '#975a16'
    },
    badgeInfo: {
      background: '#bee3f8',
      color: '#2a69ac'
    },
    navBar: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '20px',
      padding: '10px 0'
    },
    navButtons: {
      display: 'flex',
      gap: '12px',
      alignItems: 'center'
    }
  };

  // Страница входа/регистрации (без навигации)
  if (!isLoggedIn) {
    return (
      <div style={styles.container}>
        <div style={{ padding: '40px 20px', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
          <div style={styles.card}>
            <div style={{ textAlign: 'center', marginBottom: '30px' }}>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>🏋️</div>
              <h1 style={styles.title}>Тренировочная платформа</h1>
              <p style={styles.subtitle}>Автоматическое построение персональных тренировочных планов</p>
            </div>
            
            <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#2d3748', marginBottom: '16px' }}>Вход в систему</h2>
            <form onSubmit={handleLogin}>
              <input
                type="text"
                name="username"
                placeholder="👤 Логин"
                required
                style={styles.input}
                onFocus={e => e.target.style.borderColor = '#667eea'}
                onBlur={e => e.target.style.borderColor = '#e2e8f0'}
              />
              <input
                type="password"
                name="password"
                placeholder="🔒 Пароль"
                required
                style={styles.input}
                onFocus={e => e.target.style.borderColor = '#667eea'}
                onBlur={e => e.target.style.borderColor = '#e2e8f0'}
              />
              <button type="submit" style={styles.buttonPrimary} disabled={loading}>
                {loading ? '⏳ Загрузка...' : '🚀 Войти'}
              </button>
            </form>

            <hr style={{ margin: '24px 0', border: 'none', borderTop: '2px solid #e2e8f0' }} />

            <h2 style={{ fontSize: '20px', fontWeight: '600', color: '#2d3748', marginBottom: '16px' }}>Создать аккаунт</h2>
            <form onSubmit={handleRegister}>
              <input type="text" name="login" placeholder="👤 Логин" required style={styles.input} />
              <input type="email" name="email" placeholder="📧 Email" required style={styles.input} />
              <input type="password" name="password" placeholder="🔒 Пароль" required style={styles.input} />
              <input type="date" name="birth_date" required style={styles.input} />
              <select name="gender" style={styles.select}>
                <option value="male">👨 Мужской</option>
                <option value="female">👩 Женский</option>
              </select>
              <input type="number" name="weight_kg" placeholder="⚖️ Вес (кг)" required style={styles.input} />
              <input type="number" name="height_cm" placeholder="📏 Рост (см)" required style={styles.input} />
              <select name="fitness_level" style={styles.select}>
                <option value="beginner">🌱 Начинающий</option>
                <option value="intermediate">🌟 Любитель</option>
                <option value="advanced">🔥 Продвинутый</option>
              </select>
              <button type="submit" style={{ ...styles.buttonPrimary, background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)' }} disabled={loading}>
                {loading ? '⏳ Загрузка...' : '📝 Зарегистрироваться'}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Страница профиля (с навигацией)
  if (step === 'profile') {
    return (
      <div style={styles.container}>
        <div style={{ padding: '40px 20px', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
          <div style={styles.card}>
            <div style={styles.navBar}>
              <button onClick={handleLogout} style={styles.buttonDanger}>🚪 Выйти</button>
              <span style={{ fontSize: '14px', color: '#718096' }}>Шаг 1 из 3</span>
            </div>

            <div style={{ textAlign: 'center', marginBottom: '30px' }}>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>📝</div>
              <h1 style={styles.title}>Расскажите о себе</h1>
              <p style={styles.subtitle}>Для генерации плана нам нужны ваши данные</p>
            </div>
            <form onSubmit={updateProfile}>
              <label style={styles.label}>📅 Дата рождения</label>
              <input type="date" value={userData.birth_date} onChange={e => setUserData({...userData, birth_date: e.target.value})} required style={styles.input} />
              
              <label style={styles.label}>👤 Пол</label>
              <select value={userData.gender} onChange={e => setUserData({...userData, gender: e.target.value})} style={styles.select}>
                <option value="male">Мужской</option>
                <option value="female">Женский</option>
              </select>
              
              <label style={styles.label}>⚖️ Вес (кг)</label>
              <input type="number" step="0.5" value={userData.weight_kg} onChange={e => setUserData({...userData, weight_kg: e.target.value})} required style={styles.input} />
              
              <label style={styles.label}>📏 Рост (см)</label>
              <input type="number" value={userData.height_cm} onChange={e => setUserData({...userData, height_cm: e.target.value})} required style={styles.input} />
              
              <label style={styles.label}>📊 Уровень подготовки</label>
              <select value={userData.fitness_level} onChange={e => setUserData({...userData, fitness_level: e.target.value})} style={styles.select}>
                <option value="beginner">🌱 Начинающий</option>
                <option value="intermediate">🌟 Любитель</option>
                <option value="advanced">🔥 Продвинутый</option>
              </select>
              
              <label style={styles.label}>💓 Пульс покоя (опционально)</label>
              <input type="number" value={userData.rest_hr} onChange={e => setUserData({...userData, rest_hr: e.target.value})} placeholder="Например: 60" style={styles.input} />
              
              <label style={styles.label}>💓 Максимальный пульс (опционально)</label>
              <input type="number" value={userData.max_hr} onChange={e => setUserData({...userData, max_hr: e.target.value})} placeholder="Например: 190" style={styles.input} />
              
              <button type="submit" style={styles.buttonPrimary} disabled={loading}>
                {loading ? '⏳ Сохранение...' : '➡️ Далее'}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Страница выбора цели (с навигацией)
  if (step === 'goal') {
    return (
      <div style={styles.container}>
        <div style={{ padding: '40px 20px', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
          <div style={{ ...styles.card, maxWidth: '600px' }}>
            <div style={styles.navBar}>
              <div style={styles.navButtons}>
                <button onClick={() => setStep('profile')} style={styles.buttonBack}>⬅️ Назад</button>
                <button onClick={handleLogout} style={styles.buttonDanger}>🚪 Выйти</button>
              </div>
              <span style={{ fontSize: '14px', color: '#718096' }}>Шаг 2 из 3</span>
            </div>

            <div style={{ textAlign: 'center', marginBottom: '30px' }}>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>🎯</div>
              <h1 style={styles.title}>Выберите цель</h1>
              <p style={styles.subtitle}>Какую цель вы хотите достичь?</p>
            </div>
            <form onSubmit={createGoal}>
              <label style={styles.label}>🎯 Тип цели</label>
              <select value={goalData.goal_type} onChange={e => setGoalData({...goalData, goal_type: e.target.value})} style={styles.select}>
                <option value="weight_loss">⚖️ Снижение веса</option>
                <option value="endurance">🏃 Улучшение выносливости (бег)</option>
                <option value="health">❤️ Общее оздоровление</option>
              </select>
              
              {goalData.goal_type === 'weight_loss' && (
                <>
                  <label style={styles.label}>🎯 Целевой вес (кг)</label>
                  <input type="number" step="0.5" value={goalData.target_value} onChange={e => setGoalData({...goalData, target_value: e.target.value})} required style={styles.input} placeholder="Например: 70" />
                </>
              )}
              
              {goalData.goal_type === 'endurance' && (
                <>
                  <label style={styles.label}>🎯 Целевая дистанция (км)</label>
                  <select value={goalData.target_value} onChange={e => setGoalData({...goalData, target_value: e.target.value})} style={styles.select}>
                    <option value="5">5 км</option>
                    <option value="10">10 км</option>
                    <option value="21">21 км (полумарафон)</option>
                    <option value="42">42 км (марафон)</option>
                  </select>
                </>
              )}
              
              <label style={styles.label}>📅 Срок (недель)</label>
              <input type="number" value={goalData.deadline_weeks} onChange={e => setGoalData({...goalData, deadline_weeks: parseInt(e.target.value)})} style={styles.input} min="4" max="16" />
              
              <button type="submit" style={{ ...styles.buttonPrimary, background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)' }} disabled={loading}>
                {loading ? '⏳ Генерация...' : '🎯 Сгенерировать план'}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // Страница плана (с навигацией)
  const dayNames = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
  const weekCount = Object.keys(weeks).length;

  return (
    <div style={styles.container}>
      <div style={{ padding: '20px' }}>
        <div style={styles.cardWide}>
          <div style={styles.header}>
            <div>
              <span style={styles.logo}>🏋️ Тренировочная платформа</span>
              <span style={{ marginLeft: '16px', fontSize: '14px', color: '#718096' }}>Ваш персональный план</span>
            </div>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <button onClick={() => setStep('goal')} style={styles.buttonBack}>⬅️ Назад</button>
              {weekCount > 0 && (
                <span style={{ ...styles.badge, ...styles.badgeInfo }}>📅 {weekCount} недель</span>
              )}
              <button onClick={handleLogout} style={styles.buttonDanger}>🚪 Выйти</button>
            </div>
          </div>

          {weekCount > 0 && weeks[currentWeek] ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <h2 style={{ fontSize: '22px', fontWeight: '600', color: '#2d3748' }}>
                  📋 Неделя {currentWeek} из {weekCount}
                </h2>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button 
                    disabled={currentWeek === 1} 
                    onClick={() => setCurrentWeek(currentWeek - 1)}
                    style={{ ...styles.buttonSecondary, opacity: currentWeek === 1 ? 0.5 : 1, cursor: currentWeek === 1 ? 'not-allowed' : 'pointer' }}
                  >
                    ⬅️ Назад
                  </button>
                  <button 
                    disabled={currentWeek === weekCount} 
                    onClick={() => setCurrentWeek(currentWeek + 1)}
                    style={{ ...styles.buttonSecondary, opacity: currentWeek === weekCount ? 0.5 : 1, cursor: currentWeek === weekCount ? 'not-allowed' : 'pointer' }}
                  >
                    Вперёд ➡️
                  </button>
                </div>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={styles.table}>
                  <thead>
                    <tr>
                      <th style={styles.th}>📅 День</th>
                      <th style={styles.th}>🏋️ Тип</th>
                      <th style={styles.th}>⏱️ Длительность</th>
                      <th style={styles.th}>📏 Дистанция (км)</th>
                      <th style={styles.th}>⚡ Интенсивность</th>
                      <th style={styles.th}>💓 Пульс</th>
                      <th style={styles.th}>🔥 Калории</th>
                      <th style={styles.th}>📊 TRIMP</th>
                      <th style={styles.th}>⚖️ Прогноз веса</th>
                    </tr>
                  </thead>
                  <tbody>
                    {weeks[currentWeek].map((item, idx) => (
                      <tr key={idx} style={{ background: idx % 2 === 0 ? 'white' : '#f7fafc' }}>
                        <td style={styles.td}><strong>{dayNames[item.day - 1]}</strong></td>
                        <td style={styles.td}>
                          <span style={{ display: 'inline-block', padding: '4px 12px', borderRadius: '20px', background: '#ebf4ff', color: '#2a69ac', fontSize: '13px', fontWeight: '500' }}>
                            {item.workout_type || '🏃 Бег'}
                          </span>
                        </td>
                        <td style={styles.td}><strong>{item.duration_min}</strong> мин</td>
                        <td style={styles.td}>{item.distance_km ? <strong>{item.distance_km}</strong> : '-'}</td>
                        <td style={styles.td}>
                          <span style={{
                            ...styles.badge,
                            ...(item.intensity_desc === 'высокая' ? styles.badgeWarning : 
                               item.intensity_desc === 'средняя' ? styles.badgeInfo : 
                               styles.badgeSuccess)
                          }}>
                            {item.intensity_desc || 'средняя'}
                          </span>
                        </td>
                        <td style={styles.td}>{item.target_hr_zone || '-'}</td>
                        <td style={styles.td}>{item.calories ? <strong>{item.calories}</strong> : '-'}</td>
                        <td style={styles.td}>{item.trimp || '-'}</td>
                        <td style={styles.td}>
                          {item.predicted_weight ? (
                            <span style={{ fontWeight: '600', color: '#2f855a' }}>
                              {item.predicted_weight} кг
                            </span>
                          ) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div style={{ marginTop: '30px', background: '#f7fafc', borderRadius: '12px', padding: '20px' }}>
                <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#2d3748', marginBottom: '12px' }}>
                  📊 Прогресс выполнения плана
                </h4>
                <div style={{ background: '#e2e8f0', borderRadius: '10px', height: '12px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${Math.min((currentWeek / weekCount) * 100, 100)}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                    borderRadius: '10px',
                    transition: 'width 0.5s ease'
                  }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '13px', color: '#718096' }}>
                  <span>Начало</span>
                  <span>Неделя {currentWeek} из {weekCount}</span>
                  <span>Финиш 🏁</span>
                </div>
              </div>

              <div style={{ marginTop: '24px', textAlign: 'center', padding: '20px', background: '#f7fafc', borderRadius: '12px' }}>
                <p style={{ color: '#4a5568', fontSize: '15px', fontStyle: 'italic' }}>
                  💪 «Каждая тренировка — это шаг к вашей цели. Продолжайте в том же духе!»
                </p>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div style={{ fontSize: '64px', marginBottom: '20px' }}>📋</div>
              <h2 style={{ fontSize: '24px', color: '#2d3748', marginBottom: '12px' }}>План пока не сгенерирован</h2>
              <p style={{ color: '#718096', marginBottom: '24px' }}>Чтобы получить персональный план, заполните профиль и выберите цель</p>
              <button onClick={() => setStep('profile')} style={{ ...styles.buttonPrimary, width: 'auto', padding: '12px 40px' }}>
                🔄 Создать план
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;