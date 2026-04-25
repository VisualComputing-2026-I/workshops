using UnityEngine;
using UnityEngine.SceneManagement;

public class NavegacionEscenas : MonoBehaviour
{
    // Cargar por nombre de escena
    public void CargarEscena(string nombreEscena)
    {
        SceneManager.LoadScene(nombreEscena);
    }

    // Cargar por índice (útil para botones simples)
    public void CargarEscenaPorIndice(int indice)
    {
        SceneManager.LoadScene(indice);
    }

    // Salir del juego
    public void SalirJuego()
    {
        Application.Quit();
        Debug.Log("Juego cerrado"); // Solo visible en editor
    }
}