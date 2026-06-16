import React, { useState } from 'react';
import axios from 'axios';

function Register() {
  const [formData, setFormData] = useState({
    login: '',
    email: '',
    password: '',
    weight: '',
    height: '',
    gender: 'male',
    birth_date: '',
    rest_hr: '',
    max_hr: ''
  });
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsError(false);
    setMessage('');
    
    // Преобразуем дату из формата ДД.ММ.ГГГГ в ГГГГ-ММ-ДД
    let dataToSend = { ...formData };
    if (dataToSend.birth_date) {
      const parts = dataToSend.birth_date.split('.');
      if (parts.length === 3) {
        dataToSend.birth_date = `${parts[2]}-${parts[1]}-${parts[0]}`;
      }
    }
    
    try {
      const response = await axios.post('http://localhost:8000/api/auth/register', dataToSend);
      setMessage(`✅ Пользователь ${response.data.login} успешно зарегистрирован!`);
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);
    } catch (error) {
      setIsError(true);
      setMessage('❌ Ошибка: ' + (error.response?.data?.detail || 'Не удалось зарегистрироваться'));
    }
  };

  return (
    <div style={{ maxWidth: 500, margin: '50px auto', padding: 20, border: '1px solid #ccc', borderRadius: 10 }}>
      <h2>📝 Регистрация</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: 15 }}>
          <label>Логин:</label><br />
          <input type="text" name="login" value={formData.login} onChange={handleChange} style={{ width: '100%', padding: 8 }} required />
        </div>
        <div style={{ marginBottom: 15 }}>
          <label>Email:</label><br />
          <input type="email" name="email" value={formData.email} onChange={handleChange} style={{ width: '100%', padding: 8 }} required />
        </div>
        <div style={{ marginBottom: 15 }}>
          <label>Пароль:</label><br />
          <input type="password" name="password" value={formData.password} onChange={handleChange} style={{ width: '100%', padding: 8 }} required />
        </div>
        <div style={{ marginBottom: 15 }}>
          <label>Дата рождения (ДД.ММ.ГГГГ):</label><br />
          <input type="text" name="birth_date" value={formData.birth_date} onChange={handleChange} placeholder="15.06.1995" style={{ width: '100%', padding: 8 }} />
        </div>
        <div style={{ marginBottom: 15 }}>
          <label>Вес (кг):</label><br />
          <input type="number" name="weight" value={formData.weight} onChange={handleChange} style={{ width: '100%', padding: 8 }} />
        </div>
        <div style={{ marginBottom: 15 }}>
          <label>Рост (см):</label><br />
          <input type="number" name="height" value={formData.height} onChange={handleChange} style={{ width: '100%', padding: 8 }} />
        </div>
        <div style={{ marginBottom: 15 }}>
          <label>Пол:</label><br />
          <select name="gender" value={formData.gender} onChange={handleChange} style={{ width: '100%', padding: 8 }}>
            <option value="male">Мужской</option>
            <option value="female">Женский</option>
          </select>
        </div>
        <div style={{ marginBottom: 15 }}>
          <label>Пульс покоя:</label><br />
          <input type="number" name="rest_hr" value={formData.rest_hr} onChange={handleChange} style={{ width: '100%', padding: 8 }} />
        </div>
        <div style={{ marginBottom: 15 }}>
          <label>Максимальный пульс:</label><br />
          <input type="number" name="max_hr" value={formData.max_hr} onChange={handleChange} style={{ width: '100%', padding: 8 }} />
        </div>
        <button type="submit" style={{ padding: '10px 20px', background: '#28a745', color: 'white', border: 'none', borderRadius: 5, cursor: 'pointer' }}>
          Зарегистрироваться
        </button>
      </form>
      {message && (
        <p style={{ marginTop: 15, color: isError ? 'red' : 'green', textAlign: 'center' }}>
          {message}
        </p>
      )}
      <p style={{ marginTop: 15, textAlign: 'center' }}>
        <a href="/">← Назад к входу</a>
      </p>
    </div>
  );
}

export default Register;