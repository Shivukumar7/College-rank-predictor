import * as React from "react";
import { motion, HTMLMotionProps } from "framer-motion";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "success";
  size?: "default" | "sm" | "lg" | "icon";
  isLoading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "primary", size = "default", isLoading, children, ...props }, ref) => {
    let variantStyles = "";
    switch (variant) {
      case "primary":
        variantStyles = "bg-primary-900 text-white hover:bg-primary-800";
        break;
      case "secondary":
        variantStyles = "bg-primary-100 text-primary-900 hover:bg-primary-200";
        break;
      case "success":
        variantStyles = "bg-gradient-success text-white shadow-lg hover:shadow-xl hover:shadow-accent-500/20";
        break;
      case "outline":
        variantStyles = "border-2 border-primary-700 text-primary-900 hover:bg-primary-50";
        break;
      case "ghost":
        variantStyles = "hover:bg-primary-50 text-primary-900";
        break;
    }

    let sizeStyles = "";
    switch (size) {
      case "default":
        sizeStyles = "h-10 px-4 py-2";
        break;
      case "sm":
        sizeStyles = "h-9 rounded-md px-3 text-xs";
        break;
      case "lg":
        sizeStyles = "h-12 rounded-md px-8 text-lg";
        break;
      case "icon":
        sizeStyles = "h-10 w-10";
        break;
    }

    return (
      <motion.button
        ref={ref}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className={`inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-500 disabled:pointer-events-none disabled:opacity-50 ${variantStyles} ${sizeStyles} ${className}`}
        {...(props as HTMLMotionProps<"button">)}
      >
        {isLoading ? (
          <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        ) : null}
        {children}
      </motion.button>
    );
  }
);
Button.displayName = "Button";

export { Button };
