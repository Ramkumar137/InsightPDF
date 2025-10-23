import { Button } from "./button";
import { ButtonProps } from "./button";
import { forwardRef } from "react";
import { cn } from "@/lib/utils";

export const GradientButton = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, children, ...props }, ref) => (
    <Button
      ref={ref}
      className={cn(
        "bg-gradient-primary hover:shadow-glow transition-all duration-300",
        className
      )}
      {...props}
    >
      {children}
    </Button>
  )
);
GradientButton.displayName = "GradientButton";

export const GhostButton = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, children, ...props }, ref) => (
    <Button
      ref={ref}
      variant="ghost"
      className={cn(
        "hover:bg-secondary transition-all duration-200",
        className
      )}
      {...props}
    >
      {children}
    </Button>
  )
);
GhostButton.displayName = "GhostButton";
