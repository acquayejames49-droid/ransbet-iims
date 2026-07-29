from app import create_app, db
from app.models import ForecastMetric, Product
import statistics

app = create_app()
with app.app_context():
    metrics = ForecastMetric.query.all()
    
    if not metrics:
        print("No forecast metrics found. Run: python train_models.py")
        exit()
    
    print(f"Total products with metrics: {len(metrics)}")
    print()
    
    # Get accuracy per product
    product_accuracies = []
    for m in metrics:
        product = Product.query.get(m.product_id)
        name = product.name if product else f"Product {m.product_id}"
        accuracy = 100 - m.mape
        product_accuracies.append((name, accuracy, m.mape, m.mae, m.rmse))
    
    # Sort by accuracy
    product_accuracies.sort(key=lambda x: x[1])
    
    accuracies = [a[1] for a in product_accuracies]
    
    print("--- All Products (sorted by accuracy) ---")
    for i, (name, acc, mape, mae, rmse) in enumerate(product_accuracies, 1):
        print(f"{i:2}. {name:30s} | Accuracy: {acc:5.1f}% | MAPE: {mape:5.1f}% | MAE: {mae:5.1f} | RMSE: {rmse:5.1f}")
    
    print()
    print("=" * 50)
    print(f"Mean accuracy:   {statistics.mean(accuracies):.1f}%")
    print(f"Median accuracy: {statistics.median(accuracies):.1f}%")
    if len(accuracies) > 1:
        print(f"Std deviation:   {statistics.stdev(accuracies):.1f}%")
    print(f"Min: {min(accuracies):.1f}% | Max: {max(accuracies):.1f}%")
    print("=" * 50)