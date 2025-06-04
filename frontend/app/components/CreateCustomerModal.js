'use client';

import React, { useState } from 'react';

const CreateCustomerModal = ({ isOpen, onClose }) => {
  const [step, setStep] = useState(1);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [verifyPassword, setVerifyPassword] = useState('');
  const [otp, setOtp] = useState('');

  const handleNext = async () => {
    if (!email || !password || !verifyPassword) {
        alert("All fields are required.");
        return;
    }
    if (password !== verifyPassword) {
        alert("Passwords do not match.");
        return;
    }

    try {
        const res = await fetch("http://localhost:8000/customer-send-otp", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "OTP failed");
        alert("OTP sent to customer email.");
        setStep(2);
    } catch (err) {
        alert(err.message);
    }
    };


  const handleCreate = async () => {
    if (!otp) {
        alert("Please enter the OTP.");
        return;
    }

    try {
        const res = await fetch('http://localhost:8000/register-customer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, otp }),
        });

        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Registration failed");
        alert(data.message);
        handleCancel();
    } catch (err) {
        alert(err.message);
    }
    };


  const handleCancel = () => {
    setStep(1);
    setEmail('');
    setPassword('');
    setVerifyPassword('');
    setOtp('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center backdrop-blur-xs">
      <div className="bg-black p-6 rounded-xl shadow-lg w-full max-w-md">
        {step === 1 ? (
          <>
            <h2 className="text-xl font-semibold mb-4">Create Customer Account</h2>
            <input
              type="email"
              placeholder="Email"
              className="w-full mb-3 p-2 border rounded"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full mb-3 p-2 border rounded"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <input
              type="password"
              placeholder="Verify Password"
              className="w-full mb-4 p-2 border rounded"
              value={verifyPassword}
              onChange={(e) => setVerifyPassword(e.target.value)}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={handleCancel}
                className="px-4 py-2 text-md text-black font-bold bg-gray-300 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={handleNext}
                className="px-4 py-2 text-md bg-blue-600 font-bold text-white rounded hover:bg-blue-700"
              >
                Next
              </button>
            </div>
          </>
        ) : (
          <>
            <h2 className="text-xl font-semibold mb-4">Verify OTP</h2>
            <input
              type="text"
              placeholder="Enter OTP"
              className="w-full mb-4 p-2 border rounded"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={handleCancel}
                className="px-4 py-2 text-sm text-black bg-gray-300 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700"
              >
                Create Account
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CreateCustomerModal;
