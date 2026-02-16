import Link from 'next/link';
import { ShoppingBag } from 'lucide-react';

export default function Footer() {
    return (
        <footer className="border-t border-border bg-background">
            <div className="container px-4 md:px-6 py-8 md:py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <div className="space-y-4">
                        <Link href="/" className="flex items-center gap-1 group w-fit">
                            <span className="font-black text-2xl tracking-tighter text-foreground group-hover:text-primary transition-colors">
                                Bena<span className="text-primary">2</span>es
                            </span>
                        </Link>
                        <p className="text-sm text-zinc-500 dark:text-zinc-400">
                            The best deals in Egypt from Amazon, Jumia, and Noon. We track prices so you don't have to.
                        </p>
                    </div>

                    <div>
                        <h3 className="font-medium mb-4 text-zinc-900 dark:text-zinc-100">Categories</h3>
                        <ul className="space-y-2 text-sm text-zinc-500 dark:text-zinc-400">
                            <li><Link href="/category/electronics" className="hover:text-red-600">Electronics</Link></li>
                            <li><Link href="/category/fashion" className="hover:text-red-600">Fashion</Link></li>
                            <li><Link href="/category/home" className="hover:text-red-600">Home & Kitchen</Link></li>
                            <li><Link href="/category/all" className="hover:text-red-600">All Categories</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-medium mb-4 text-zinc-900 dark:text-zinc-100">Company</h3>
                        <ul className="space-y-2 text-sm text-zinc-500 dark:text-zinc-400">
                            <li><Link href="/about" className="hover:text-red-600">About Us</Link></li>
                            <li><Link href="/contact" className="hover:text-red-600">Contact</Link></li>
                            <li><Link href="/privacy" className="hover:text-red-600">Privacy Policy</Link></li>
                            <li><Link href="/terms" className="hover:text-red-600">Terms of Service</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-medium mb-4 text-zinc-900 dark:text-zinc-100">Legal</h3>
                        <p className="text-sm text-zinc-500 dark:text-zinc-400">
                            Sooq Deals is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.eg.
                        </p>
                    </div>
                </div>

                <div className="mt-8 pt-8 border-t border-zinc-200 dark:border-zinc-800 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-xs text-muted-foreground">
                        &copy; {new Date().getFullYear()} Bena2es. All rights reserved.
                    </p>
                    <div className="flex gap-4">
                        {/* Social links placeholder */}
                    </div>
                </div>
            </div>
        </footer>
    );
}
