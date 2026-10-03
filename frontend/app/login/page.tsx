import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-sm rounded-xl border border-border bg-card p-6">
        <div className="mb-6 flex items-center gap-2">
          <span aria-hidden className="size-2.5 rounded-full bg-primary" />
          <h1 className="text-base font-semibold tracking-tight">Karma Farming Autobot</h1>
        </div>
        <LoginForm />
      </div>
    </main>
  );
}
