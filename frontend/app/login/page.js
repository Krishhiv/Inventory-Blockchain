'use client'
import React, { useState } from 'react'
import { useRouter } from "next/navigation"

const Page = () => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")

  const router = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/emp-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");

      setError("");
      router.push(`/emp-otp?email=${encodeURIComponent(email)}`);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-400">
      <div className="bg-white border-gray-300 p-8 rounded-2xl shadow-lg w-full max-w-md">
        <h1 className="text-2xl text-gray-800 font-bold mb-6 text-center">Login</h1>

        {error && (
          <p className="text-red-600 text-sm font-semibold mb-4 text-center">{error}</p>
        )}

        <form className="space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="block text-gray-800 text-sm font-bold mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-black text-black rounded-md p-2 focus:outline-none focus:ring-2 
              focus:ring-blue-600"
              placeholder="example@email.com"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-800 font-bold mb-1">Password</label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-black text-black rounded-md p-2 pr-20 focus:outline-none 
                focus:ring-2 focus:ring-blue-600"
                placeholder="Enter your password"
              />
              <button
                type="button"
                onClick={() => setShowPassword((prev) => !prev)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-sm font-bold text-gray-700 hover:text-black 
                transition-colors duration-300 cursor-pointer"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>
          <button
            type="submit"
            className="w-full mt-4 py-2 font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-md  
            transition duration-300 transform active:scale-95 active:opacity-80 
            focus:outline-none cursor-pointer"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  )
}

export default Page
