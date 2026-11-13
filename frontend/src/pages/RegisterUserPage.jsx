import { useState } from 'react';

function RegisterUserPage() {
  const [message, setMessage] = useState("");

  async function registerUser(username, password, role) {
    const res = await fetch("http://127.0.0.1:8000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username, password: password, role: role })
    });
    const data = await res.json();
    if (res.ok) {
      setMessage(data.message);
    } else {
      setMessage(data.detail);
    }
  }

  return (
    <>
      <h2>Register</h2>
      <button onClick={() => registerUser("Bhuvan", "Bhuvan123", "admin")}>
        Register Bhuvan (Admin)
      </button>
      <button onClick={() => registerUser("Karthik", "Karthik123", "staff")}>
        Register Karthik (Staff)
      </button>
      <p>{message}</p>
    </>
  );
}

export default RegisterUserPage;