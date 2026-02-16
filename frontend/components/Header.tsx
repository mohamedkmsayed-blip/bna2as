'use client';

import Link from 'next/link';
import { Search, Menu, ShoppingBag } from 'lucide-react';
import { useState } from 'react';

export default function Header() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <header className="sticky top-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-16 items-center px-4 md:px-6">
                {/* Mobile Menu Button */}
                <button
                    className="mr-4 md:hidden p-2 hover:bg-zinc-100 dark:hover:bg-zinc-800 rounded-md"
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                >
                    <Menu className="h-5 w-5" />
                    <span className="sr-only">Toggle menu</span>
                </button>

                {/* Logo */}
                <Link href="/" className="mr-6 flex items-center gap-1 group">
                    <span className="font-black text-2xl tracking-tighter text-foreground group-hover:text-primary transition-colors">
                        Bena<span className="text-primary">2</span>es
                    </span>
                </Link>

                {/* Desktop Navigation */}
                <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
                    <Link href="/deals" className="transition-colors hover:text-zinc-900/80 text-zinc-900/60 dark:text-zinc-400 dark:hover:text-zinc-50">
                        All Deals
                    </Link>
                    <Link href="/category/electronics" className="transition-colors hover:text-zinc-900/80 text-zinc-900/60 dark:text-zinc-400 dark:hover:text-zinc-50">
                        Electronics
                    </Link>
                    <Link href="/category/fashion" className="transition-colors hover:text-zinc-900/80 text-zinc-900/60 dark:text-zinc-400 dark:hover:text-zinc-50">
                        Fashion
                    </Link>
                    <Link href="/category/home" className="transition-colors hover:text-zinc-900/80 text-zinc-900/60 dark:text-zinc-400 dark:hover:text-zinc-50">
                        Home
                    </Link>
                </nav>

                {/* Search Bar (Placeholder) */}
                <div className="flex flex-1 items-center justify-end space-x-4">
                    <div className="w-full flex-1 md:w-auto md:flex-none">
                        <div className="relative">
                            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-zinc-500 dark:text-zinc-400" />
                            <input
                                type="search"
                                placeholder="Search deals..."
                                className="h-9 w-full rounded-md border border-zinc-200 bg-white px-8 py-2 text-sm outline-none placeholder:text-zinc-500 focus:border-zinc-900 focus:ring-1 focus:ring-zinc-900 dark:border-zinc-800 dark:bg-zinc-950 dark:placeholder:text-zinc-400 dark:focus:border-zinc-50 dark:focus:ring-zinc-50 md:w-[200px] lg:w-[300px]"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            {isMenuOpen && (
                <div className="md:hidden border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950">
                    <nav className="flex flex-col space-y-4 p-4">
                        <Link href="/deals" className="text-sm font-medium hover:text-red-600">
                            All Deals
                        </Link>
                        <Link href="/category/electronics" className="text-sm font-medium hover:text-red-600">
                            Electronics
                        </Link>
                        <Link href="/category/fashion" className="text-sm font-medium hover:text-red-600">
                            Fashion
                        </Link>
                        <Link href="/category/home" className="text-sm font-medium hover:text-red-600">
                            Home
                        </Link>
                    </nav>
                </div>
            )}
        </header>
    );
}
