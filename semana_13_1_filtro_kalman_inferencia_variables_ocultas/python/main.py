import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)
n = 100

# --- Datos sintéticos ---
real = np.cumsum(np.random.randn(n))          # Posición real (caminata aleatoria)
observed = real + np.random.normal(0, 2, n)   # Observación con ruido gaussiano

# --- Parámetros del filtro ---
Q = 1.0     # Ruido del proceso (varianza) — refleja la dinámica de la caminata aleatoria
R = 4.0     # Ruido de medición (varianza)

# --- Filtro de Kalman 1D ---
x_hat, P = 0.0, 1.0
estimate = np.empty(n)

for i, z in enumerate(observed):
    # Predicción
    x_prior = x_hat
    P_prior = P + Q

    # Ganancia de Kalman y corrección
    K = P_prior / (P_prior + R)
    x_hat = x_prior + K * (z - x_prior)
    P = (1 - K) * P_prior

    estimate[i] = x_hat

# --- Métricas ---
rmse_obs = np.sqrt(np.mean((observed - real) ** 2))
rmse_est = np.sqrt(np.mean((estimate - real) ** 2))
print(f"RMSE observado: {rmse_obs:.4f}")
print(f"RMSE estimado (Kalman): {rmse_est:.4f}")
print(f"Mejora: {(1 - rmse_est / rmse_obs) * 100:.1f}%")

# --- Visualización ---
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Gráfico principal: las tres señales
ax = axes[0]
ax.plot(real, label="Real", color="#2196F3", linewidth=1.5)
ax.plot(observed, label="Observado (ruidoso)", color="#FF9800",
        alpha=0.5, linewidth=0.8, linestyle="--")
ax.plot(estimate, label="Estimado (Kalman)", color="#4CAF50", linewidth=1.8)
ax.fill_between(range(n), estimate - 2, estimate + 2,
                alpha=0.15, color="#4CAF50", label="±1σ estimado")
ax.set_title("Filtro de Kalman 1D — Estimación de posición oculta", fontsize=14)
ax.set_xlabel("Paso de tiempo")
ax.set_ylabel("Posición")
ax.legend(loc="upper left")
ax.grid(True, alpha=0.3)

# Gráfico de errores
ax2 = axes[1]
ax2.plot(np.abs(observed - real), label=f"Error observado (RMSE={rmse_obs:.2f})",
         color="#FF9800", alpha=0.6, linewidth=0.9)
ax2.plot(np.abs(estimate - real), label=f"Error Kalman (RMSE={rmse_est:.2f})",
         color="#4CAF50", linewidth=1.2)
ax2.set_title("Error absoluto por paso de tiempo")
ax2.set_xlabel("Paso de tiempo")
ax2.set_ylabel("|Error|")
ax2.legend(loc="upper left")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("kalman_plot.png", dpi=150, bbox_inches="tight")
plt.show()
print("Gráfico guardado como kalman_plot.png")