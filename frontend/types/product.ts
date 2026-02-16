export interface Product {
    id: string;
    source: 'amazon' | 'jumia' | 'noon';
    external_id: string;
    title: string;
    image: string | null;
    category: string | null;
    url: string;
    affiliate_url: string | null;
    current_price: number;
    original_price: number | null;
    discount_pct: number | null;
    rating: number | null;
    review_count: number | null;
    in_stock: number;
    is_active: number;
}
