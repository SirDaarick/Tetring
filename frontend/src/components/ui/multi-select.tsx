import { useState, useRef, useEffect } from "react";
import { Check, ChevronDown, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface MultiSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
}

export function MultiSelect({ options, selected, onChange, placeholder = "Select..." }: MultiSelectProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleOption = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter((item) => item !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  const clearOption = (e: React.MouseEvent, option: string) => {
    e.stopPropagation();
    onChange(selected.filter((item) => item !== option));
  };

  return (
    <div className="relative w-full" ref={containerRef}>
      <div 
        className="flex min-h-10 w-full items-center justify-between rounded-2xl border-0 bg-[#f4f1fa] px-3 py-2 text-sm shadow-clay-input focus-within:ring-2 focus-within:ring-clay-primary focus-within:ring-offset-2 cursor-pointer"
        onClick={() => setOpen(!open)}
      >
        <div className="flex flex-wrap gap-1">
          {selected.length === 0 && <span className="text-muted-foreground">{placeholder}</span>}
          {selected.map((item) => (
            <Badge key={item} variant="secondary" className="mr-1 mb-1 flex items-center gap-1 px-2 py-0.5 font-normal">
              {item}
              <div 
                className="ml-1 rounded-full outline-none hover:bg-black/20 cursor-pointer"
                onClick={(e) => clearOption(e, item)}
              >
                <X className="h-3 w-3" />
              </div>
            </Badge>
          ))}
        </div>
        <ChevronDown className="h-4 w-4 opacity-50 flex-shrink-0" />
      </div>
      
      {open && (
        <div className="absolute top-full z-50 mt-1 max-h-60 w-full overflow-auto rounded-clay border-0 bg-white/95 shadow-clay-lg backdrop-blur-md p-1">
          {options.length === 0 ? (
            <div className="py-6 text-center text-sm text-muted-foreground">No options available</div>
          ) : (
            options.map((option) => (
              <div
                key={option}
                className="relative flex cursor-pointer select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                onClick={() => toggleOption(option)}
              >
                <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
                  {selected.includes(option) && <Check className="h-4 w-4" />}
                </span>
                {option}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
