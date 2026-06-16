import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState(null);
  const [step, setStep] = useState('login');
  const [weeks, setWeeks] = useState({});
  const [currentWeek, setCurrentWeek] = useState(1);
  const [userData, setUserData] = useState({
    birth_date: '', gender: 'male', weight_kg: '', height_cm: '',
    fitness_level: 'beginner', rest_hr: '', max_hr: ''
  });
  const [goalData, setGoalData] = useState({
    goal_type: 'weight_loss', target_value: 65, deadline_weeks: 8
  });

  const api = axios.create({ baseURL: 'http://localhost:8000/api' });

  api.interceptors.request.use((config) => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      config.headers.Authorization = `Bearer ${savedToken}`;
    }
    return config;
  });

  const getIntensityClass = (level) => {
    if (level === 'высокая') return '#ef4444';
    if (level === 'средняя') return '#f59e0b';
    return '#10b981';
  };
  const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
      const response = await api.post('/auth/login', {
        username: formData.get('username'),
        password: formData.get('password')
      }, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
      localStorage.setItem('token', response.data.access_token);
      setToken(response.data.access_token);
      setIsLoggedIn(true);
      setStep('profile');
      alert('Вход выполнен успешно!');
    } catch (error) { 
      alert('Ошибка входа: ' + (error.response?.data?.detail || 'Неверный логин или пароль'));
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
      await api.post('/auth/register', {
        login: formData.get('login'), email: formData.get('email'), password: formData.get('password'),
        birth_date: formData.get('birth_date'), gender: formData.get('gender'),
        weight_kg: parseFloat(formData.get('weight_kg')), height_cm: parseFloat(formData.get('height_cm')),
        fitness_level: formData.get('fitness_level')
      });
      alert('Регистрация успешна! Теперь войдите.');
    } catch (error) { 
      alert('Ошибка регистрации: ' + (error.response?.data?.detail || 'Попробуйте другой логин'));
    }
  };

  const updateProfile = async (e) => {
    e.preventDefault();
    
    if (!userData.birth_date) {
      alert('Укажите дату рождения');
      return;
    }
    if (!userData.weight_kg || userData.weight_kg <= 0) {
      alert('Укажите корректный вес');
      return;
    }
    if (!userData.height_cm || userData.height_cm <= 0) {
      alert('Укажите корректный рост');
      return;
    }
    
    let birthDate = userData.birth_date;
    if (birthDate && birthDate.includes('.')) {
      const parts = birthDate.split('.');
      if (parts.length === 3) {
        birthDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
      }
    }
    
    try {
      const payload = {
        birth_date: birthDate,
        gender: userData.gender,
        weight_kg: parseFloat(userData.weight_kg),
        height_cm: parseFloat(userData.height_cm),
        fitness_level: userData.fitness_level,
        rest_hr: userData.rest_hr ? parseInt(userData.rest_hr) : null,
        max_hr: userData.max_hr ? parseInt(userData.max_hr) : null
      };
      
      await api.post('/plan/update-profile', payload);
      setStep('goal');
    } catch (error) { 
      alert('Ошибка сохранения профиля: ' + (error.response?.data?.detail || 'Неизвестная ошибка')); 
    }
  };

  const createGoal = async (e) => {
    e.preventDefault();
    try {
      let dataToSend = { ...goalData };
      if (dataToSend.goal_type === 'health') {
        dataToSend.target_value = 0;
      } else {
        dataToSend.target_value = parseFloat(dataToSend.target_value);
      }
      dataToSend.deadline_weeks = parseInt(dataToSend.deadline_weeks);
      await api.post('/plan/create-goal', dataToSend);
      setStep('plan');
      const response = await api.post('/plan/generate');
      const weeksMap = {};
      response.data.plan.forEach(item => {
        if (!weeksMap[item.week]) weeksMap[item.week] = [];
        weeksMap[item.week].push(item);
      });
      setWeeks(weeksMap);
    } catch (error) { 
      alert('Ошибка создания цели');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setIsLoggedIn(false);
    setStep('login');
  };

  const handleBackToGoal = () => {
    setStep('goal');
  };

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      setIsLoggedIn(true);
      setStep('profile');
    }
  }, []);

  // Стили с чёрным фоном для select
  const inputStyle = {
    width: '100%',
    padding: '12px 16px',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '16px',
    color: '#ffffff',
    fontSize: '1rem',
    boxSizing: 'border-box'
  };

  const selectStyle = {
    width: '100%',
    padding: '12px 16px',
    backgroundColor: '#1a1a2e',
    border: '1px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '16px',
    color: '#ffffff',
    fontSize: '1rem',
    boxSizing: 'border-box',
    cursor: 'pointer'
  };

  const buttonStyle = {
    background: 'linear-gradient(135deg, #a855f7, #06b6d4)',
    border: 'none',
    borderRadius: '40px',
    padding: '12px 28px',
    color: 'white',
    fontWeight: '600',
    fontSize: '1rem',
    cursor: 'pointer',
    width: '100%'
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '8px',
    fontWeight: '500',
    color: 'rgba(255, 255, 255, 0.9)'
  };

  const cardStyle = {
    background: 'rgba(255, 255, 255, 0.08)',
    backdropFilter: 'blur(12px)',
    borderRadius: '24px',
    padding: '32px',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
  };

  // Страница входа/регистрации
  if (!isLoggedIn) {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
        <div style={{ ...cardStyle, maxWidth: '500px', width: '100%' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: '700', textAlign: 'center', background: 'linear-gradient(135deg, #fff, #a855f7, #06b6d4)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', marginBottom: '30px' }}>
            🏋️ Персональный тренер
          </h1>
          <h3 style={{ color: '#c084fc', marginBottom: '15px' }}>Вход</h3>
          <form onSubmit={handleLogin}>
            <div style={{ marginBottom: '16px' }}><input type="text" name="username" placeholder="Логин" required style={inputStyle} /></div>
            <div style={{ marginBottom: '16px' }}><input type="password" name="password" placeholder="Пароль" required style={inputStyle} /></div>
            <button type="submit" style={buttonStyle}>Войти</button>
          </form>
          <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.15)', margin: '20px 0' }} />
          <h3 style={{ color: '#c084fc', marginBottom: '15px' }}>Регистрация</h3>
          <form onSubmit={handleRegister}>
            <div style={{ marginBottom: '12px' }}><input type="text" name="login" placeholder="Логин" required style={inputStyle} /></div>
            <div style={{ marginBottom: '12px' }}><input type="email" name="email" placeholder="Email" required style={inputStyle} /></div>
            <div style={{ marginBottom: '12px' }}><input type="password" name="password" placeholder="Пароль" required style={inputStyle} /></div>
            <div style={{ marginBottom: '12px' }}><input type="date" name="birth_date" required style={inputStyle} /></div>
            <div style={{ marginBottom: '12px' }}>
              <select name="gender" required style={selectStyle}>
                <option value="male">Мужской</option>
                <option value="female">Женский</option>
              </select>
            </div>
            <div style={{ marginBottom: '12px' }}><input type="number" step="0.5" name="weight_kg" placeholder="Вес (кг)" required style={inputStyle} /></div>
            <div style={{ marginBottom: '12px' }}><input type="number" step="0.5" name="height_cm" placeholder="Рост (см)" required style={inputStyle} /></div>
            <div style={{ marginBottom: '12px' }}>
              <select name="fitness_level" style={selectStyle}>
                <option value="beginner">Начинающий</option>
                <option value="intermediate">Любитель</option>
                <option value="advanced">Продвинутый</option>
              </select>
            </div>
            <button type="submit" style={buttonStyle}>Зарегистрироваться</button>
          </form>
        </div>
      </div>
    );
  }

  // Страница профиля
  if (step === 'profile') {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
        <div style={{ ...cardStyle, maxWidth: '550px', width: '100%', position: 'relative' }}>
          <button onClick={handleLogout} style={{ position: 'absolute', top: '20px', right: '20px', background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '40px', padding: '6px 12px', color: 'white', cursor: 'pointer', fontSize: '12px' }}>Выйти</button>
          <h1 style={{ fontSize: '2rem', fontWeight: '700', textAlign: 'center', background: 'linear-gradient(135deg, #fff, #a855f7, #06b6d4)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', marginBottom: '30px' }}>
            📝 Расскажите о себе
          </h1>
          <form onSubmit={updateProfile}>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Дата рождения (ДД.ММ.ГГГГ)</label><input type="text" placeholder="21.03.2002" value={userData.birth_date} onChange={e => setUserData({...userData, birth_date: e.target.value})} required style={inputStyle} /></div>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Пол</label>
              <select value={userData.gender} onChange={e => setUserData({...userData, gender: e.target.value})} style={selectStyle}>
                <option value="male">Мужской</option>
                <option value="female">Женский</option>
              </select>
            </div>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Вес (кг)</label><input type="number" step="0.5" value={userData.weight_kg} onChange={e => setUserData({...userData, weight_kg: e.target.value})} required style={inputStyle} /></div>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Рост (см)</label><input type="number" step="0.5" value={userData.height_cm} onChange={e => setUserData({...userData, height_cm: e.target.value})} required style={inputStyle} /></div>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Уровень подготовки</label>
              <select value={userData.fitness_level} onChange={e => setUserData({...userData, fitness_level: e.target.value})} style={selectStyle}>
                <option value="beginner">Начинающий</option>
                <option value="intermediate">Любитель</option>
                <option value="advanced">Продвинутый</option>
              </select>
            </div>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Пульс покоя (опционально)</label><input type="number" value={userData.rest_hr} onChange={e => setUserData({...userData, rest_hr: e.target.value})} style={inputStyle} /></div>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Максимальный пульс (опционально)</label><input type="number" value={userData.max_hr} onChange={e => setUserData({...userData, max_hr: e.target.value})} style={inputStyle} /></div>
            <button type="submit" style={buttonStyle}>Далее →</button>
          </form>
        </div>
      </div>
    );
  }

  // Страница выбора цели
  if (step === 'goal') {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
        <div style={{ ...cardStyle, maxWidth: '650px', width: '100%', position: 'relative' }}>
          <button onClick={handleLogout} style={{ position: 'absolute', top: '20px', right: '20px', background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '40px', padding: '6px 12px', color: 'white', cursor: 'pointer', fontSize: '12px' }}>Выйти</button>
          <h1 style={{ fontSize: '2rem', fontWeight: '700', textAlign: 'center', background: 'linear-gradient(135deg, #fff, #a855f7, #06b6d4)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', marginBottom: '30px' }}>
            🎯 Какую цель вы хотите достичь?
          </h1>
          <form onSubmit={createGoal}>
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Тип цели</label>
              <select value={goalData.goal_type} onChange={e => setGoalData({...goalData, goal_type: e.target.value})} style={selectStyle}>
                <option value="weight_loss">⚖️ Снижение веса</option>
                <option value="endurance">🏃 Улучшение выносливости (бег)</option>
                <option value="health">❤️ Общее оздоровление</option>
              </select>
            </div>
            {goalData.goal_type === 'weight_loss' && (
              <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Целевой вес (кг)</label><input type="number" step="0.5" value={goalData.target_value} onChange={e => setGoalData({...goalData, target_value: e.target.value})} required style={inputStyle} /></div>
            )}
            {goalData.goal_type === 'endurance' && (
              <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Целевая дистанция (км)</label>
                <select value={goalData.target_value} onChange={e => setGoalData({...goalData, target_value: e.target.value})} style={selectStyle}>
                  <option value="5">5 км</option><option value="10">10 км</option><option value="21">21 км (полумарафон)</option><option value="42">42 км (марафон)</option>
                </select>
              </div>
            )}
            <div style={{ marginBottom: '16px' }}><label style={labelStyle}>Срок (недель)</label><input type="number" value={goalData.deadline_weeks} onChange={e => setGoalData({...goalData, deadline_weeks: parseInt(e.target.value)})} style={inputStyle} /></div>
            <button type="submit" style={buttonStyle}>🎯 Сгенерировать план</button>
          </form>
        </div>
      </div>
    );
  }

  // Главная страница с планом тренировок
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f0c29, #302b63, #24243e)', padding: '30px 20px' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <button onClick={handleBackToGoal} style={{ background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '40px', padding: '10px 20px', color: 'white', cursor: 'pointer' }}>← Назад</button>
            <h1 style={{ fontSize: '2rem', fontWeight: '700', background: 'linear-gradient(135deg, #fff, #a855f7, #06b6d4)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>
              🏋️ Ваш персональный план
            </h1>
          </div>
          <button onClick={handleLogout} style={{ background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '40px', padding: '10px 20px', color: 'white', cursor: 'pointer' }}>Выйти</button>
        </div>

        {Object.keys(weeks).length > 0 && weeks[currentWeek] ? (
          <div style={cardStyle}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ color: '#c084fc', margin: 0 }}>Неделя {currentWeek}</h2>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button disabled={currentWeek === 1} onClick={() => setCurrentWeek(prev => prev - 1)} style={{ background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '40px', padding: '8px 16px', color: 'white', cursor: 'pointer' }}>← Назад</button>
                <button disabled={currentWeek === Object.keys(weeks).length} onClick={() => setCurrentWeek(prev => prev + 1)} style={{ background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '40px', padding: '8px 16px', color: 'white', cursor: 'pointer' }}>Вперёд →</button>
              </div>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>День</th>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>Тип</th>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>Длит.</th>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>Дист. (км)</th>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>Интенс.</th>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>Ккал</th>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>TRIMP</th>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>Пульс</th>
                    <th style={{ padding: '14px 16px', textAlign: 'left', color: 'white' }}>Прогноз веса</th>
                  </tr>
                </thead>
                <tbody>
                  {weeks[currentWeek].map((item, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                      <td style={{ padding: '12px 16px', color: 'rgba(255,255,255,0.9)' }}>{weekDays[item.day - 1]}</td>
                      <td style={{ padding: '12px 16px', color: 'rgba(255,255,255,0.9)' }}>{item.workout_type}</td>
                      <td style={{ padding: '12px 16px', color: 'rgba(255,255,255,0.9)' }}>{item.duration_min} мин</td>
                      <td style={{ padding: '12px 16px', color: 'rgba(255,255,255,0.9)' }}>{item.distance_km || '-'}</td>
                      <td style={{ padding: '12px 16px', color: getIntensityClass(item.intensity_desc), fontWeight: 'bold' }}>{item.intensity_desc}</td>
                      <td style={{ padding: '12px 16px', color: 'rgba(255,255,255,0.9)' }}>{item.calories || '-'}</td>
                      <td style={{ padding: '12px 16px', color: 'rgba(255,255,255,0.9)' }}>{item.trimp || '-'}</td>
                      <td style={{ padding: '12px 16px', color: 'rgba(255,255,255,0.9)' }}>{item.target_hr_zone || '-'}</td>
                      <td style={{ padding: '12px 16px', color: 'rgba(255,255,255,0.9)' }}>{item.predicted_weight ? `${item.predicted_weight} кг` : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div style={cardStyle}>
            <p style={{ textAlign: 'center', color: 'rgba(255,255,255,0.7)' }}>Загрузка плана тренировок...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;