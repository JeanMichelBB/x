import { useState, useEffect } from 'react';
import axios from "axios";
import './Signup.css';
import { Link } from "react-router-dom";
import User from "../../UserModel";
import { faker } from '@faker-js/faker';
import { apiUrl } from '../../api';

const Signup = () => {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("password");
  const [email, setEmail] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("password");
  const [error, setError] = useState<string>("");
  const [users, setUsers] = useState<User[]>([]);
  const [initialUsername, setInitialUsername] = useState<string>("");
  const [initialEmail, setInitialEmail] = useState<string>("");
  const currentDate = new Date();
  const formattedDate = currentDate.toISOString().slice(0, 19).replace('T', ' '); 

  const generateUniqueUsername = () => {
    const existingUsernames = users.map((user) => user.username);
    let suggestedUsername;
    do {
      suggestedUsername = faker.internet.username();
    } while (existingUsernames.includes(suggestedUsername));
    return suggestedUsername;
  };

  const generateUniqueEmail = () => {
    let email = "";
    do {
      email = faker.internet.email();
    } while (users.some(user => user.email === email));
    return email;
  };

  const generateUniquePassword = () => {
    return "password"; // Generate your password logic here
  };

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await fetch(`${apiUrl}/users`);
        if (!response.ok) {
          throw new Error('Failed to fetch users');
        }
        const data = await response.json();
        setUsers(data);
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    };
    fetchUsers();
  }, []);

  useEffect(() => {
    if (users.length > 0) {
      const newUsername = generateUniqueUsername();
      const newEmail = generateUniqueEmail();
      setUsername(newUsername);
      setInitialUsername(newUsername);
      setEmail(newEmail);
      setInitialEmail(newEmail);
      const newPassword = generateUniquePassword();
      setPassword(newPassword);
      setConfirmPassword(newPassword);
    }
  }, [users]);


  const handleSignup = async () => {
    try {
      if (password !== confirmPassword) {
        setError("Passwords do not match");
        return;
      }

      if (username !== initialUsername || email !== initialEmail) {
        setError("Invalid username or email");
        return;
      }

      if (password !== generateUniquePassword() || confirmPassword !== generateUniquePassword()) {
        setError("Invalid password or confirm password");
        return;
      }

      const response = await axios.post(`${apiUrl}/signup`, {
        username,
        email,
        password,
        date_joined: formattedDate,
      });
      if (response.status !== 200) {
        throw new Error('Failed to signup');
      }

      window.location.href = "/login";
    } catch (err) {
      setError("Error signing up");
      console.error("Signup error:", err);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-logo">
        X
      </div>
      <div className="signup-form">
        <h2>Signup</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
        <button onClick={handleSignup}>
          Signup
        </button>
        {error && <div>{error}</div>}
        <p>Already have an account? <Link to="/login">Login</Link></p>
      </div>
    </div>
  );
};

export default Signup;
