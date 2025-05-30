'use client';
import React, { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'

const OTPPage = () => {
  const [otp, setOtp] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const router = useRouter()
  const searchParams = useSearchParams()
  const email = searchParams.get("email")

  useEffect(() => {
    if (!email) {
      setError("Missing email. Please login again.")
    }
  }, [email])

  const handleVerify = async (e) => {
    e.preventDefault()

    if (!otp || !email) {
      setError("Please enter the OTP.")
      return
    }

    try {
      const res = await fetch("http://localhost:8000/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp }),
      })

      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || "OTP verification failed")

      // ✅ Store the token
      localStorage.setItem("access_token", data.access_token)

      setError("")
      setSuccess("Login successful!")

      setTimeout(() => {
        router.push("/dashboard")
      }, 1500)
    } catch (err) {
      setError(err.message)
      setSuccess("")
    }
  }


  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-400">
      <div className="bg-white border-gray-300 p-8 rounded-2xl shadow-lg w-full max-w-md">
        <h1 className="text-2xl text-gray-800 font-bold mb-6 text-center">Enter OTP</h1>

        {error && <p className="text-red-600 text-sm font-semibold mb-4 text-center">{error}</p>}
        {success && <p className="text-green-600 text-sm font-semibold mb-4 text-center">{success}</p>}

        <form className="space-y-4" onSubmit={handleVerify}>
          <div>
            <label className="block text-gray-800 text-sm font-bold mb-1">OTP</label>
            <input
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="w-full border border-black text-black rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
              placeholder="Enter the OTP sent to your email"
            />
          </div>

          <button
            type="submit"
            className="w-full mt-4 py-2 font-bold bg-blue-600 hover:bg-blue-700 text-white rounded-md transition duration-300 transform active:scale-95 active:opacity-80 focus:outline-none cursor-pointer"
          >
            Verify OTP
          </button>
        </form>
      </div>
    </div>
  )
}

export default OTPPage
