"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { User, Eye, EyeOff, Shield, Lock, CheckCircle2 } from "lucide-react"
import { useRouter } from "next/navigation"

const AnimatedBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 bg-gradient-to-br from-[#e8ecf5] via-[#f0f3fa] to-[#e8ecf5]" />
      <motion.div
        className="absolute top-20 left-20 w-64 h-64 bg-gradient-to-br from-pink-200/30 to-purple-200/30 rounded-full blur-3xl"
        animate={{
          x: [0, 100, 0],
          y: [0, 50, 0],
        }}
        transition={{
          duration: 20,
          repeat: Number.POSITIVE_INFINITY,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-br from-blue-200/30 to-cyan-200/30 rounded-full blur-3xl"
        animate={{
          x: [0, -100, 0],
          y: [0, -50, 0],
        }}
        transition={{
          duration: 25,
          repeat: Number.POSITIVE_INFINITY,
          ease: "easeInOut",
        }}
      />
    </div>
  )
}

const SecurityIndicator: React.FC<{ isActive: boolean }> = ({ isActive }) => {
  return (
    <motion.div
      className="absolute top-4 right-4 flex items-center gap-2"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: isActive ? 1 : 0.5, scale: isActive ? 1 : 0.9 }}
      transition={{ duration: 0.3 }}
    >
      <motion.div
        animate={{
          rotate: isActive ? 360 : 0,
        }}
        transition={{
          duration: 2,
          repeat: isActive ? Number.POSITIVE_INFINITY : 0,
          ease: "linear",
        }}
      >
        <Shield className="w-5 h-5 text-pink-500" />
      </motion.div>
      <span className="text-xs font-mono text-gray-500">{isActive ? "Encrypted" : "Secure"}</span>
    </motion.div>
  )
}

const AvatarPlaceholder: React.FC = () => {
  return (
    <motion.div
      className="w-20 h-20 rounded-full bg-[#f0f3fa] flex items-center justify-center mb-8 shadow-[inset_8px_8px_16px_#d1d9e6,inset_-8px_-8px_16px_#ffffff]"
      whileHover={{ scale: 1.05 }}
      transition={{ type: "spring", stiffness: 400 }}
    >
      <User className="w-8 h-8 text-gray-400" />
    </motion.div>
  )
}

interface InputFieldProps {
  type: string
  placeholder: string
  value: string
  onChange: (value: string) => void
  showPasswordToggle?: boolean
  icon?: React.ReactNode
}

const InputField: React.FC<InputFieldProps> = ({
  type,
  placeholder,
  value,
  onChange,
  showPasswordToggle = false,
  icon,
}) => {
  const [showPassword, setShowPassword] = useState(false)
  const [isFocused, setIsFocused] = useState(false)
  const [isSecure, setIsSecure] = useState(false)
  const inputType = showPasswordToggle ? (showPassword ? "text" : "password") : type

  useEffect(() => {
    if (isFocused && value.length > 0) {
      const timer = setTimeout(() => setIsSecure(true), 500)
      return () => clearTimeout(timer)
    } else {
      setIsSecure(false)
    }
  }, [isFocused, value])

  return (
    <motion.div
      className="relative mb-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {icon && <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400">{icon}</div>}
      <motion.input
        type={inputType}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        className={`w-full ${icon ? "pl-12" : "pl-6"} pr-12 py-4 bg-[#f0f3fa] rounded-2xl text-gray-700 placeholder-gray-400 outline-none transition-all duration-200 font-mono ${
          isFocused
            ? "shadow-[inset_6px_6px_12px_#d1d9e6,inset_-6px_-6px_12px_#ffffff] ring-2 ring-pink-500/30"
            : "shadow-[inset_8px_8px_16px_#d1d9e6,inset_-8px_-8px_16px_#ffffff]"
        }`}
        animate={{
          filter: isFocused && value.length > 0 ? "blur(0px)" : "blur(0px)",
        }}
      />
      <AnimatePresence>
        {isSecure && (
          <motion.div
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0 }}
            className="absolute right-12 top-1/2 transform -translate-y-1/2"
          >
            <CheckCircle2 className="w-5 h-5 text-green-500" />
          </motion.div>
        )}
      </AnimatePresence>
      {showPasswordToggle && (
        <motion.button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
        </motion.button>
      )}
    </motion.div>
  )
}

interface LoginButtonProps {
  onClick: () => void
  isLoading: boolean
}

const LoginButton: React.FC<LoginButtonProps> = ({ onClick, isLoading }) => {
  return (
    <motion.button
      type="submit"
      onClick={onClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`w-full py-4 bg-gradient-to-r from-pink-500 to-purple-500 rounded-2xl text-white text-lg mb-6 shadow-[8px_8px_16px_#d1d9e6,-8px_-8px_16px_#ffffff] hover:shadow-[6px_6px_12px_#d1d9e6,-6px_-6px_12px_#ffffff] transition-all duration-200 font-mono font-semibold ${
        isLoading ? "opacity-50 cursor-not-allowed" : ""
      }`}
      disabled={isLoading}
      animate={{
        background: isLoading
          ? "linear-gradient(90deg, #ec4899 0%, #a855f7 100%)"
          : "linear-gradient(90deg, #ec4899 0%, #8b5cf6 50%, #a855f7 100%)",
      }}
    >
      {isLoading ? (
        <motion.span
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY }}
        >
          Authenticating...
        </motion.span>
      ) : (
        "Login Securely"
      )}
    </motion.button>
  )
}

const FooterLinks: React.FC = () => {
  return (
    <div className="flex justify-between items-center text-sm">
      <motion.button
        className="text-gray-500 hover:text-pink-500 transition-all duration-200 font-mono"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Forgot password?
      </motion.button>
      <motion.button
        className="text-gray-500 hover:text-pink-500 transition-all duration-200 font-mono"
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Sign up
      </motion.button>
    </div>
  )
}

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isFormActive, setIsFormActive] = useState(false)
  const router = useRouter()

  useEffect(() => {
    setIsFormActive(email.length > 0 || password.length > 0)
  }, [email, password])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!email || !password) {
      return
    }

    if (!email.includes("@")) {
      return
    }

    setIsLoading(true)

    await new Promise((resolve) => setTimeout(resolve, 2000))

    localStorage.setItem(
      "mastomysUser",
      JSON.stringify({
        email,
        loginTime: new Date().toISOString(),
      }),
    )

    router.push("/monitoring")
  }

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center relative overflow-hidden">
      <AnimatedBackground />

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="relative z-10"
      >
        <motion.h1
          className="text-4xl text-center font-mono font-black text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-600 mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          Mastomys Tracker
        </motion.h1>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="w-full max-w-md mx-auto bg-[#f0f3fa] rounded-3xl p-8 shadow-[20px_20px_40px_#d1d9e6,-20px_-20px_40px_#ffffff] relative"
        >
          <SecurityIndicator isActive={isFormActive} />

          <div className="flex flex-col items-center">
            <AvatarPlaceholder />

            <motion.h2
              className="text-2xl font-mono font-bold text-gray-700 mb-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              Secure Access
            </motion.h2>

            <form onSubmit={handleSubmit} className="w-full">
              <InputField
                type="email"
                placeholder="Email"
                value={email}
                onChange={setEmail}
                icon={<User className="w-5 h-5" />}
              />

              <InputField
                type="password"
                placeholder="Password"
                value={password}
                onChange={setPassword}
                showPasswordToggle={true}
                icon={<Lock className="w-5 h-5" />}
              />

              <LoginButton onClick={handleSubmit} isLoading={isLoading} />
            </form>

            <FooterLinks />
          </div>

          <motion.div
            className="mt-6 text-center text-xs font-mono text-gray-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            End-to-end encrypted connection
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  )
}
