import DealCard from '@/components/DealCard';
import FilterSidebar from '@/components/FilterSidebar';
import { Product } from '@/types/product';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mohamed-kmsayed--sooq-deals-api.modal.run/api/deals';

async function getDeals(): Promise<Product[]> {
  try {
    const res = await fetch(API_URL, { next: { revalidate: 60 } });
    if (!res.ok) {
      throw new Error('Failed to fetch data');
    }
    const data = await res.json();
    return data.items || [];
  } catch (error) {
    console.error('Error fetching deals:', error);
    return [];
  }
}

export default async function Home() {
  const deals = await getDeals();

  return (
    <div className="container px-4 md:px-6 py-6 md:py-8">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar (Desktop) */}
        <div className="w-64 flex-shrink-0 hidden md:block">
          <FilterSidebar />
        </div>

        {/* Main Content */}
        <div className="flex-1">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-3xl font-black text-foreground tracking-tight">
              Latest Hot Deals
            </h1>
            <div className="text-sm text-zinc-500 dark:text-zinc-400">
              Showing {deals.length} results
            </div>
          </div>

          {deals.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {deals.map((product) => (
                <DealCard key={product.id} product={product} />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-zinc-200 flex flex-col items-center justify-center">
              <div className="bg-zinc-50 p-4 rounded-full mb-4">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="48"
                  height="48"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="text-zinc-400"
                >
                  <path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z" /><path d="M3 6h18" /><path d="M16 10a4 4 0 0 1-8 0" />
                </svg>
              </div>
              <p className="text-lg font-medium text-zinc-900">No deals found yet</p>
              <p className="text-sm text-zinc-500 mt-1 max-w-xs mx-auto">
                We're scouring the web for the best discounts. Check back in a few minutes!
              </p>
            </div>
          )}

          {/* Pagination Placeholder */}
          {deals.length > 0 && (
            <div className="mt-12 flex justify-center">
              <button className="px-6 py-2 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-md text-sm font-medium hover:bg-zinc-50 dark:hover:bg-zinc-700 transition-colors">
                Load More
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
