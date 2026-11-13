import { useState } from 'react';

function LoginPage({ setToken }) {
  const [message, setMessage] = useState("");

  async function loginUser(username, password) {
    const res = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username, password: password })
    });
    const data = await res.json();
    if (res.ok) {
      setToken(data.access_token);
      setMessage("Logged in as " + username + " (" + data.role + ")");
    } else {
      setMessage(data.detail);
    }
  }

  return (
    <>
      <h2>Login</h2>
      <button onClick={() => loginUser("Soham", "123456")}>
        Login Soham (Admin)
      </button>
      <p>{message}</p>
    </>
  );
}

export default LoginPage;