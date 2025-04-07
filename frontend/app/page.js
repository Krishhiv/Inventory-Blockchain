'use client'
import React, { useState } from 'react'

const Page = () => {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [otp, setOtp] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")

  const handleLogin = (e) => {
    e.preventDefault() // Prevent form reload

    // Basic validation
    if (!name || !email || !password || !otp) {
      setError("Please fill in all fields.")
      return
    }

    setError("") // Clear previous error

    // You now have access to all input values:
    console.log(name);
    console.log(email);
    console.log(password);
    console.log(otp);

    // Proceed with login logic (API calls etc.)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-400">
      <div className="bg-white border-gray-300 p-8 rounded-2xl shadow-lg w-full max-w-md">
        <h1 className="text-2xl text-gray-800 font-bold mb-6 text-center">Login</h1>

        {error && (
          <p className="text-red-600 text-sm font-semibold mb-4 text-center">{error}</p>
        )}

        <form className="space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="block text-gray-800 text-sm font-bold mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border border-black text-black rounded-md p-2 focus:outline-none focus:ring-2 
              focus:ring-blue-600"
              placeholder="Your Name"
            />
          </div>

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

          <div className="flex items-center gap-2">
            <input
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="flex-grow border border-black text-black rounded-md p-2 focus:outline-none focus:ring-2 
              focus:ring-blue-600"
              placeholder="Enter OTP"
            />
            <button
              type="button"
              className="px-4 py-2 font-bold bg-slate-700 text-white rounded-md hover:bg-slate-800 
              transition-colors duration-300 cursor-pointer"
            >
              Send OTP
            </button>
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
