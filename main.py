from utils.file_handler import (
    read_sales_data, 
    parse_transactions, 
    validate_and_filter
)
from utils.data_processor import (
    calculate_total_revenue, 
    region_wise_sales, 
    top_selling_products, 
    customer_analysis, 
    daily_sales_trend, 
    find_peak_sales_day, 
    low_performing_products
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data,
    save_enriched_data
)
from pathlib import Path
from datetime import datetime

def format_currency(value):
    return f"₹{value:,.2f}"

def divider(char='=', length=50):
    return char * length

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    base = Path(__file__).parent
    data_path = base / output_file

    total_records = len(transactions)
    total_revenue = calculate_total_revenue(transactions)
    avg_order_value = total_revenue / total_records if total_records > 0 else 0.0

    # Date range
    dates = [record['Date'] for record in transactions]
    start_date = min(dates)
    end_date = max(dates)
    
    with open(data_path, 'w', encoding='utf-8') as f:
        
        # =====================================================
        # 1. HEADER
        # =====================================================
        f.write(divider() + '\n')
        f.write("SALES ANALYTICS REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Records Processed: {total_records}\n")
        f.write(divider() + "\n\n")


        # =====================================================
        # 2. OVERALL SUMMARY
        # =====================================================
        f.write("OVERALL SUMMARY\n")
        f.write(divider('-') + "\n")
        f.write(f"Total Revenue: {format_currency(total_revenue)}\n")
        f.write(f"Total Transactions: {total_records}\n")
        f.write(f"Average Order Value: {format_currency(avg_order_value)}\n")
        f.write(f"Date Range: {start_date} to {end_date}\n\n")


        # =====================================================
        # 3. REGION-WISE PERFORMANCE
        # =====================================================
        f.write("REGION-WISE PERFORMANCE\n")
        f.write(divider('-') + "\n")

        region_stats = region_wise_sales(transactions)

        # Table header
        f.write(f"{'Region':<10}{'Sales':>15}{'% of Total':>15}{'Transactions':>15}\n")
        f.write(divider('-') + "\n")

        for region, stats in region_stats.items():
            sales = format_currency(stats['total_sales'])
            percentage = f"{stats['percentage']:.2f}%"
            txn_count = stats['transaction_count']

            f.write(f"{region:<10}{sales:>15}{percentage:>15}{txn_count:>15}\n")

        f.write("\n")


        # =====================================================
        # 4. TOP 5 PRODUCTS
        # =====================================================
        f.write("TOP 5 PRODUCTS\n")
        f.write(divider('-') + "\n")

        top_products = top_selling_products(transactions, n=5)

        # Table header
        f.write(f"{'Rank':<6}{'Product Name':<20}{'Quantity Sold':>15}{'Revenue':>15}\n")
        f.write(divider('-') + "\n")

        for idx, (product, quantity, revenue) in enumerate(top_products, start=1):
            f.write(
                f"{idx:<6}"
                f"{product:<20}"
                f"{quantity:>15}"
                f"{format_currency(revenue):>15}\n"
            )

        f.write("\n")


        # =====================================================
        # 5. TOP 5 CUSTOMERS
        # =====================================================
        f.write("TOP 5 CUSTOMERS\n")
        f.write(divider('-') + "\n")

        customer_stats = customer_analysis(transactions)

        # Table header
        f.write(f"{'Rank':<6}{'Customer ID':<15}{'Total Spent':>20}{'Order Count':>15}\n")
        f.write(divider('-') + "\n")

        for idx, (customer_id, stats) in enumerate(list(customer_stats.items())[:5], start=1):
            total_spent = format_currency(stats['total_spent'])
            order_count = stats['purchase_count']

            f.write(
                f"{idx:<6}"
                f"{customer_id:<15}"
                f"{total_spent:>20}"
                f"{order_count:>15}\n"
            )

        f.write("\n")


        # =====================================================
        # 6. DAILY SALES TREND
        # =====================================================
        f.write("DAILY SALES TREND\n")
        f.write(divider('-') + "\n")

        daily_trends = daily_sales_trend(transactions)

        # Table header
        f.write(
            f"{'Date':<15}"
            f"{'Revenue':>20}"
            f"{'Transactions':>15}"
            f"{'Unique Customers':>20}\n"
        )
        f.write(divider('-') + "\n")

        for date, stats in daily_trends.items():
            revenue = format_currency(stats['revenue'])
            txn_count = stats['transaction_count']
            unique_customers = stats['unique_customers']

            f.write(
                f"{date:<15}"
                f"{revenue:>20}"
                f"{txn_count:>15}"
                f"{unique_customers:>20}\n"
            )

        f.write("\n")


        # =====================================================
        # 7. PRODUCT PERFORMANCE ANALYSIS
        # =====================================================
        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write(divider('-') + "\n")

        # ---- Best Selling Day ----
        peak_date, peak_revenue, peak_txn_count = find_peak_sales_day(transactions)

        f.write("Peak Sales Day\n")
        f.write(divider('.') + "\n")
        f.write(f"Date: {peak_date}\n")
        f.write(f"Total Revenue: {format_currency(peak_revenue)}\n")
        f.write(f"Transaction Count: {peak_txn_count}\n\n")

        # ---- Low Performing Products ----
        f.write("Low Performing Products\n")
        f.write(divider('.') + "\n")

        low_products = low_performing_products(transactions)

        if not low_products:
            f.write("No low-performing products found.\n\n")
        else:
            f.write(f"{'Product Name':<25}{'Quantity Sold':>15}{'Revenue':>15}\n")
            f.write(divider('.') + "\n")

            for product, quantity, revenue in low_products:
                f.write(
                    f"{product:<25}"
                    f"{quantity:>15}"
                    f"{format_currency(revenue):>15}\n"
                )
            f.write("\n")

        # ---- Average Transaction Value per Region ----
        f.write("Average Transaction Value by Region\n")
        f.write(divider('.') + "\n")

        region_stats = region_wise_sales(transactions)

        f.write(f"{'Region':<15}{'Avg Transaction Value':>25}\n")
        f.write(divider('.') + "\n")

        for region, stats in region_stats.items():
            avg_value = stats['total_sales'] / stats['transaction_count']
            f.write(
                f"{region:<15}"
                f"{format_currency(avg_value):>25}\n"
            )

        f.write("\n")


        # =====================================================
        # 8. API ENRICHMENT SUMMARY
        # =====================================================
        f.write("API ENRICHMENT SUMMARY\n")
        f.write(divider('-') + "\n")

        total_enriched = len(enriched_transactions)
        matched = sum(1 for txn in enriched_transactions if txn.get('API_Match'))
        not_matched = total_enriched - matched
        match_percentage = (matched / total_enriched * 100) if total_enriched > 0 else 0.0

        f.write(f"Total Products Enriched: {total_enriched}\n")
        f.write(f"API Matches Found: {matched}\n")
        f.write(f"API Matches Not Found: {not_matched}\n")
        f.write(f"Success Rate Percentage: {match_percentage:.2f}%\n\n")


    print(f"Sales report generated at {data_path}")

def main():
    try:
        print(divider())
        print("SALES ANALYTICS SYSTEM")
        print(divider())

        # [1/10] Read sales data
        print("\n[1/10] Reading sales data...")
        raw_lines = read_sales_data("sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions")

        # [2/10] Parse and clean data
        print("\n[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records")

        # [3/10] Display filter options
        print("\n[3/10] Filter Options Available:")
        regions = sorted({record['Region'] for record in transactions})
        amounts = [record['Quantity'] * record['UnitPrice'] for record in transactions]

        print(f"Regions: {', '.join(regions)}")
        print(f"Amount Range: ₹{min(amounts):,.0f} to ₹{max(amounts):,.0f}")

        apply_filter = input("\nDo you want to filter data? (y/n): ").strip().lower()

        if apply_filter == 'y':
            region = input("Enter region (or press Enter to skip): ").strip() or None

            min_amount = input("Enter minimum amount (or press Enter to skip): ").strip()
            min_amount = float(min_amount) if min_amount else None

            max_amount = input("Enter maximum amount (or press Enter to skip): ").strip()
            max_amount = float(max_amount) if max_amount else None
        else:
            region = min_amount = max_amount = None

        # [4/10] Validate and filter
        print("\n[4/10] Validating transactions...")
        valid_txns, invalid_count, summary = validate_and_filter(
            transactions,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount
        )
        print(f"✓ Valid: {len(valid_txns)} | Invalid: {invalid_count}")

        # [5/10] Analysis (implicit via functions)
        print("\n[5/10] Analyzing sales data...")
        _ = calculate_total_revenue(valid_txns)
        print("✓ Analysis complete")

        # [6/10] Fetch API data
        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        product_mapping = create_product_mapping(api_products)
        print(f"✓ Fetched {len(api_products)} products")

        # [7/10] Enrich sales data
        print("\n[7/10] Enriching sales data...")
        enriched_txns = enrich_sales_data(valid_txns, product_mapping)
        matched = sum(1 for record in enriched_txns if record['API_Match'])
        print(f"✓ Enriched {matched}/{len(enriched_txns)} transactions "
              f"({matched/len(enriched_txns)*100:.1f}%)")
        
        # [8/10] Save enriched data
        print("\n[8/10] Saving enriched data...")
        save_enriched_data(enriched_txns)
        print("✓ Saved to data/enriched_sales_data.txt")

        # [9/10] Generate report
        print("\n[9/10] Generating report...")
        generate_sales_report(valid_txns, enriched_txns)
        print("✓ Report saved to output/sales_report.txt")

        # [10/10] Done
        print("\n[10/10] Process Complete!")
        print(divider())
    
    except Exception as err:
        print("\nAn error occurred during execution!")
        print(f"Details: {err}")


if __name__ == "__main__":
    main()

