import { useState, useEffect } from 'react';
import { useParams } from 'react-router';

function PackageDetailPage({ token }) {
  const { id } = useParams();
  const [pkg, setPkg] = useState(null);
  const [message, setMessage] = useState("Loading");

  useEffect(() => {
    async function loadPackage() {
      const res = await fetch(`http://127.0.0.1:8000/packages/${id}`, {
        headers: { token: token }
      });
      if (res.ok) {
        const data = await res.json();
        setPkg(data);
        setMessage("");
      } else {
        setMessage("Package not found");
      }
    }
    loadPackage();
  }, [id, token]);

  async function updateStatus() {
    const res = await fetch(`http://127.0.0.1:8000/packages/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        token: token
      },
      body: JSON.stringify({ status: "dispatched" })
    });
    const data = await res.json();
    setPkg(data);
  }

  async function deletePackage() {
    const res = await fetch(`http://127.0.0.1:8000/packages/${id}`, {
      method: "DELETE",
      headers: { token: token }
    });
    const data = await res.json();
    if (res.ok) {
      setPkg(null);
      setMessage("Deleted");
    } else {
      setMessage(data.detail);
    }
  }

  if (!pkg) return <p>{message}</p>;

  return (
    <>
      <h2>{pkg.name}</h2>
      <p>Destination: {pkg.destination}</p>
      <p>Weight: {pkg.weight} kg</p>
      <p>Status: {pkg.status}</p>

      <button onClick={updateStatus}>Dispatch</button>
      <button onClick={deletePackage}>Delete</button>
      <p>{message}</p>
    </>
  );
}

export default PackageDetailPage;