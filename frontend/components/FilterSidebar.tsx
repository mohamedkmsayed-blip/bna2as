'use client';

// Using 'SlidersHorizontal' instead of 'Filter'
import { SlidersHorizontal, X } from 'lucide-react';
import { useState } from 'react';

// Price range constants
const MIN_PRICE = 0;
const MAX_PRICE = 50000;

export default function FilterSidebar() {
    const [priceRange, setPriceRange] = useState<[number, number]>([MIN_PRICE, MAX_PRICE]);
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            {/* Mobile Toggle */}
            <button
                className="md:hidden flex items-center gap-2 mb-4 px-4 py-2 bg-zinc-100 dark:bg-zinc-800 rounded-lg text-sm font-medium"
                onClick={() => setIsOpen(!isOpen)}
            >
                <SlidersHorizontal className="w-4 h-4" /> Filters
            </button>

            {/* Sidebar Content */}
            <aside className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-card border-r border-border p-6 transform transition-transform duration-300 ease-in-out md:relative md:transform-none md:block shadow-sm md:shadow-none
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
                <div className="flex justify-between items-center mb-6 md:hidden">
                    <h2 className="font-bold text-lg">Filters</h2>
                    <button onClick={() => setIsOpen(false)}>
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="space-y-8">
                    {/* Source Filter */}
                    <div>
                        <h3 className="font-medium mb-3 text-sm uppercase tracking-wide text-zinc-500">Store</h3>
                        <div className="space-y-2">
                            {['Amazon', 'Jumia', 'Noon'].map((store) => (
                                <label key={store} className="flex items-center gap-2 cursor-pointer group">
                                    <input type="checkbox" className="rounded border-input text-primary focus:ring-primary" defaultChecked />
                                    <span className="text-sm text-foreground group-hover:text-primary transition-colors">{store}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Category Filter */}
                    <div>
                        <h3 className="font-medium mb-3 text-sm uppercase tracking-wide text-zinc-500">Category</h3>
                        <div className="space-y-2">
                            {['Electronics', 'Fashion', 'Home & Kitchen', 'Beauty', 'Sports'].map((cat) => (
                                <label key={cat} className="flex items-center gap-2 cursor-pointer group">
                                    <input type="checkbox" className="rounded border-input text-primary focus:ring-primary" />
                                    <span className="text-sm text-foreground group-hover:text-primary transition-colors">{cat}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Discount Filter */}
                    <div>
                        <h3 className="font-medium mb-3 text-sm uppercase tracking-wide text-zinc-500">Min Discount</h3>
                        <div className="space-y-2">
                            {[15, 30, 50, 70].map((d) => (
                                <label key={d} className="flex items-center gap-2 cursor-pointer group">
                                    <input type="radio" name="discount" className="text-primary focus:ring-primary" />
                                    <span className="text-sm text-foreground group-hover:text-primary transition-colors">{d}% off or more</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Price Range Filter (Stub) */}
                    <div>
                        <h3 className="font-medium mb-3 text-sm uppercase tracking-wide text-zinc-500">Price Range</h3>
                        <div className="flex items-center gap-2 text-sm text-zinc-600">
                            <span>Soon</span>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Overlay for mobile */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-30 md:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}
        </>
    );
}
