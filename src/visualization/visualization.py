import matplotlib.pyplot as plt
import os

def plot_histograms(df):
    numeric_columns = df.select_dtypes(include=['number'])
    numeric_columns.hist(bins=20, figsize=(20, 20))
    plt.title("Histograms of numerical columns")
    plt.tight_layout()
    save_path = "./reports/figures"
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, "histograms.png"))
    plt.close()

def plot_comparison(train_dates, train_data, test_dates, y_pred_inverse, y_test_inverse, model_name, color1, color2, mae, mse, evs):
    plt.figure(figsize=(20, 6))
    plt.title(f'Razpoložljiva stojala {model_name}\nMAE: {mae:.2f}, MSE: {mse:.2f}, EVS: {evs:.2f}')
    plt.xlabel('Datum')
    plt.ylabel('Kolesarska stojala')
    plt.xticks(rotation=45)
    plt.plot(test_dates, y_test_inverse, color='purple', label='Dejanske vrednosti')
    plt.plot(test_dates, y_pred_inverse, color=color2, label=f'Napoved')
    plt.plot(train_dates, train_data, color=color1, label='Učna množica')
    plt.legend()
    plt.tight_layout()
    save_path = "./reports/figures"
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, "comparison.png"))
    plt.close()

def plot_model_history(history):
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Learning History')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.tight_layout()
    save_path = "./reports/figures"
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(os.path.join(save_path, "model_history.png"))
    plt.close()
