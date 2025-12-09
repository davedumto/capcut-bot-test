'use client';

interface FooterProps {
  onBookSlot: () => void;
}

export function Footer({ onBookSlot }: FooterProps) {
  return (
    <footer className="w-full py-12 px-4 border-t border-white/5 bg-background">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="flex items-center gap-2">
          <span className="font-display text-2xl font-bold text-white tracking-tight">
            Slotio
          </span>
        </div>

        <div className="flex items-center gap-8 text-sm font-medium text-white/60">
          <button onClick={onBookSlot} className="hover:text-primary transition-colors">
            Book a Slot
          </button>
          <a href="#how-it-works" className="hover:text-primary transition-colors">
            How It Works
          </a>
          <a href="#pricing" className="hover:text-primary transition-colors">
            Pricing
          </a>
        </div>

        <div className="flex flex-col items-end gap-2 text-right">
          <a href="mailto:help@slotio.io" className="text-white/80 hover:text-primary transition-colors text-sm">
            help@slotio.io
          </a>
          <p className="text-white/40 text-xs">
            © 2024 Slotio. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
