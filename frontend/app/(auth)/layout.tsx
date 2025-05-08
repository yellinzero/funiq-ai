import AuthHeader from '@/app/(auth)/components/AuthHeader'

export default function AuthLayout(props: {
  children: React.ReactNode
}) {
  const { children } = props

  return (
    <main className="flex bg-background overflow-auto items-center justify-center size-full">
      <AuthHeader />

      <div className="flex-1 flex items-center justify-center flex-col gap-4">
        {children}
      </div>
    </main>
  )
}
