/**
 * AI Council - Button Component
 * Basic reusable button component
 */
import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
  loading?: boolean
  children: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  loading = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'px-4 py-2.5 rounded-xl font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 active:scale-[0.98]'
  
  const variantStyles = {
    primary: 'bg-[#123c52] text-white shadow-lg shadow-[#123c52]/15 hover:-translate-y-0.5 hover:bg-[#1b536c] focus:ring-[#42cdb3] disabled:bg-[#8ca8b3]',
    secondary: 'border border-[#d7e3e8] bg-white text-[#315469] hover:-translate-y-0.5 hover:border-[#42cdb3] hover:bg-[#e8faf5] focus:ring-[#42cdb3] disabled:bg-[#eef3f5]',
    danger: 'bg-[#e2775f] text-white shadow-lg shadow-[#e2775f]/15 hover:-translate-y-0.5 hover:bg-[#c9624d] focus:ring-[#e2775f] disabled:bg-[#d9a094]',
  }

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? 'Loading...' : children}
    </button>
  )
}
