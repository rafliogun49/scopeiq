import { Button as ButtonPrimitive } from "@base-ui/react/button";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-2xl border border-transparent bg-clip-padding font-geist text-sm font-semibold tracking-tight whitespace-nowrap outline-none select-none transition-all duration-200 ease-out active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:translate-y-0 disabled:opacity-45 aria-invalid:border-red-300 aria-invalid:ring-3 aria-invalid:ring-red-200/70 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default:
          "bg-emerald-700 text-white shadow-[0_14px_32px_-18px_rgba(4,120,87,0.9)] ring-1 ring-emerald-500/20 hover:-translate-y-0.5 hover:bg-emerald-800 hover:shadow-[0_20px_44px_-22px_rgba(4,120,87,0.95)] focus-visible:ring-4 focus-visible:ring-emerald-200",
        outline:
          "border-slate-200/80 bg-white/85 text-slate-700 shadow-[0_12px_28px_-24px_rgba(15,23,42,0.7)] hover:-translate-y-0.5 hover:border-emerald-200 hover:bg-emerald-50/60 hover:text-emerald-800 focus-visible:ring-4 focus-visible:ring-emerald-100",
        secondary:
          "border-slate-200/80 bg-slate-100 text-slate-800 hover:-translate-y-0.5 hover:bg-slate-200/80 focus-visible:ring-4 focus-visible:ring-slate-200",
        ghost:
          "text-slate-600 hover:bg-slate-100 hover:text-slate-950 focus-visible:ring-4 focus-visible:ring-slate-200",
        destructive:
          "border-red-200/80 bg-red-50 text-red-700 hover:-translate-y-0.5 hover:bg-red-100 hover:text-red-800 focus-visible:ring-4 focus-visible:ring-red-100",
        link: "rounded-md px-0 text-emerald-800 underline-offset-4 hover:text-emerald-900 hover:underline",
      },
      size: {
        default:
          "h-10 gap-2 px-4 has-data-[icon=inline-end]:pr-3.5 has-data-[icon=inline-start]:pl-3.5",
        xs: "h-7 gap-1.5 rounded-xl px-2.5 text-xs has-data-[icon=inline-end]:pr-2 has-data-[icon=inline-start]:pl-2 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-8 gap-1.5 rounded-xl px-3 text-[0.8rem] has-data-[icon=inline-end]:pr-2.5 has-data-[icon=inline-start]:pl-2.5 [&_svg:not([class*='size-'])]:size-3.5",
        lg: "h-11 gap-2 px-5 text-[0.95rem] has-data-[icon=inline-end]:pr-4 has-data-[icon=inline-start]:pl-4",
        icon: "size-10",
        "icon-xs": "size-7 rounded-xl [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-8 rounded-xl",
        "icon-lg": "size-11",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonPrimitive.Props & VariantProps<typeof buttonVariants>) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
}

export { Button, buttonVariants };
