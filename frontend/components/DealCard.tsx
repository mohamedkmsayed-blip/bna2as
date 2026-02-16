'use client';

import Image from 'next/image';
import Link from 'next/link';
import { Star, ExternalLink } from 'lucide-react';
import { Product } from '@/types/product';

interface DealCardProps {
    product: Product;
}

const SOURCE_COLORS = {
    amazon: 'bg-orange-500',
    jumia: 'bg-orange-600', // Jumia uses orange too, slightly different
    noon: 'bg-yellow-400 text-black',
};

const SOURCE_LABELS = {
    amazon: 'Amazon',
    jumia: 'Jumia',
    noon: 'Noon',
};

export default function DealCard({ product }: DealCardProps) {
    const discount = product.discount_pct ? Math.round(product.discount_pct) : 0;
    const sourceColor = SOURCE_COLORS[product.source as keyof typeof SOURCE_COLORS] || 'bg-gray-500';
    const sourceLabel = SOURCE_LABELS[product.source as keyof typeof SOURCE_LABELS] || product.source;

    return (
        <div className="group relative bg-card text-card-foreground rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 border border-border flex flex-col h-full">
            {/* Image Container */}
            <div className="relative aspect-square w-full bg-white p-4 flex items-center justify-center overflow-hidden">
                {product.image ? (
                    <Image
                        src={product.image}
                        alt={product.title}
                        fill
                        className="object-contain group-hover:scale-105 transition-transform duration-300"
                        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                    />
                ) : (
                    <div className="w-full h-full bg-gray-100 dark:bg-zinc-800 flex items-center justify-center text-gray-400">
                        No Image
                    </div>
                )}

                {/* Discount Badge */}
                {discount > 0 && (
                    <div className="absolute top-2 left-2 bg-accent text-accent-foreground text-xs font-bold px-2 py-1 rounded-md shadow-sm">
                        -{discount}%
                    </div>
                )}

                {/* Source Badge */}
                <div className={`absolute top-2 right-2 ${sourceColor} text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm capitalize opacity-90`}>
                    {sourceLabel}
                </div>
            </div>

            {/* Content */}
            <div className="p-4 flex flex-col flex-grow">
                <Link href={`/go/${product.id}`} target="_blank" className="group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    <h3 className="font-medium text-sm text-zinc-900 dark:text-zinc-100 line-clamp-2 h-10 mb-2" title={product.title}>
                        {product.title}
                    </h3>
                </Link>

                {/* Rating */}
                <div className="flex items-center gap-1 mb-3">
                    <div className="flex text-yellow-500">
                        {[...Array(5)].map((_, i) => (
                            <Star
                                key={i}
                                size={12}
                                fill={i < Math.round(product.rating || 0) ? "currentColor" : "none"}
                                className={i < Math.round(product.rating || 0) ? "text-yellow-400" : "text-gray-300 dark:text-zinc-700"}
                            />
                        ))}
                    </div>
                    <span className="text-xs text-zinc-500 dark:text-zinc-400 ml-1">
                        ({product.review_count?.toLocaleString() || 0})
                    </span>
                </div>

                <div className="mt-auto">
                    {/* Prices */}
                    <div className="flex items-baseline gap-2 mb-3">
                        <span className="text-xl font-bold text-primary">
                            EGP {product.current_price.toLocaleString()}
                        </span>
                        {product.original_price && (
                            <span className="text-xs text-zinc-500 dark:text-zinc-400 line-through">
                                EGP {product.original_price.toLocaleString()}
                            </span>
                        )}
                    </div>

                    {/* CTA Button */}
                    <Link
                        href={`/go/${product.id}`}
                        target="_blank"
                        className="flex items-center justify-center w-full gap-2 bg-success text-success-foreground hover:bg-success/90 font-bold text-sm py-3 rounded-xl transition-all shadow-sm hover:shadow-md"
                    >
                        Get Deal <ExternalLink size={14} />
                    </Link>
                </div>
            </div>
        </div>
    );
}
