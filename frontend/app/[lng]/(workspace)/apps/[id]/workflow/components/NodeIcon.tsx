'use client'

// TODO wait Node Icon design
interface NodeIconProps {
  label: string
  children?: React.ReactNode
}

export default function NodeIcon({ label, children }: NodeIconProps) {
  if (children) {
    return children
  }

  return (
    <div
      className="bg-blue-500 rounded size-5 text-white flex items-center justify-center"
    >
      {label?.[0]?.toUpperCase()}
    </div>
  )
}
