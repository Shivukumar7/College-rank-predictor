import * as React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  glass?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className = "", glass = false, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={`flex h-10 w-full rounded-md border px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-500 disabled:cursor-not-allowed disabled:opacity-50 transition-colors
          ${
            glass
              ? "bg-white/10 border-white/20 text-white placeholder:text-white/60 backdrop-blur-md"
              : "border-primary-700 bg-white text-primary-900 placeholder:text-primary-600"
          } 
          ${className}`}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
