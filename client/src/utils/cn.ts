import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

// clsx allow write conditional classes in tailwind
// twMerge use last parameter 
// for exp: twMerge('p-4', 'p-2') result: "p-2" 

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}