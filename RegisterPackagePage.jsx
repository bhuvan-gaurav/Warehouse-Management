import { useState } from 'react';
import { Link } from 'react-router';

function RegisterPackagePage({ token }) {
  const [pkg, setPkg] = useState(null);

  async function registerPackage(name, destination, weight) {
    const res = await fetch("http://127.0.0.1:8000/packages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        token: token
      },
      body: JSON.stringify({ name: name, destination: destination, weight: weight })
    });
    const data = await res.json();
    if (res.ok) {
      setPkg(data);
    }
  }

  return (
    <>
      <h2>Register Package</h2>
      <button onClick={() => registerPackage("Electronics Box", "Mumbai", 5.5)}>
        Add Electronics Box
      </button>
      <button onClick={() => registerPackage("Medical Supplies", "Delhi", 2.0)}>
        Add Medical Supplies
      </button>

      {pkg && (
        <div>
          <p>{pkg.name} : {pkg.destination} ({pkg.status})</p>
          <Link to={`/packages/${pkg.id}`}>View Details</Link>
        </div>
      )}
    </>
  );
}

export default RegisterPackagePage;