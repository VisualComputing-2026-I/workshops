using UnityEngine;
using UnityEngine.UI;

public class ForwardKinematics : MonoBehaviour
{

    public Transform brazo1;   
    public Transform brazo2;   
    public Transform pinza;    
    public Transform extremo;  

    public Slider sliderB1;
    public Slider sliderB2;
    public Slider sliderPinza;
    public Toggle toggleAnimacion;          

    public float amplitudB1    = 60f;
    public float amplitudB2    = 40f;
    public float amplitudPinza = 20f;

    public float velocidadB1    = 0.8f;
    public float velocidadB2    = 1.2f;
    public float velocidadPinza = 1.5f;

    public bool mostrarTrayectoria = true;
    public int  maxPuntos          = 300;
    public Color colorLinea        = Color.cyan;

    private Vector3[] _puntos;
    private int       _indice = 0;
    private bool      _lleno  = false;

    void Start()
    {
        _puntos = new Vector3[maxPuntos];
        ActualizarUI(toggleAnimacion.isOn);                      // ← estado inicial
        toggleAnimacion.onValueChanged.AddListener(ActualizarUI); // ← escucha cambios
    }

    void ActualizarUI(bool animando)
    {
        sliderB1.interactable    = !animando;
        sliderB2.interactable    = !animando;
        sliderPinza.interactable = !animando;
    }

    void Update()
    {
        if (toggleAnimacion.isOn)
            AnimarArticulaciones();
        else
            MoverArticulaciones();

        RegistrarTrayectoria();

        if (mostrarTrayectoria)
            DibujarTrayectoria();
    }

    void MoverArticulaciones()
    {
        // BRAZO1 rota en Z (elevación del primer segmento)
        float anguloB1 = sliderB1.value*180;
        brazo1.localEulerAngles = new Vector3(0f, 0f, anguloB1);

        // BRAZO2 rota en Z con desfase de fase (π/3) para movimiento más orgánico
        float anguloB2 = sliderB2.value*180;
        brazo2.localEulerAngles = new Vector3(0f, 0f, anguloB2);

        // PINZA rota en X (abre/cierra en otro eje)
        float anguloPinza = sliderPinza.value*180;
        pinza.localEulerAngles = new Vector3(anguloPinza, 0f, 0f);
    }

    // ─── Animación ────────────────────────────────────────────────
    void AnimarArticulaciones()
    {
        float t = Time.time;

        // BRAZO1 rota en Z (elevación del primer segmento)
        float anguloB1 = Mathf.Sin(t * velocidadB1) * amplitudB1;
        brazo1.localEulerAngles = new Vector3(0f, 0f, anguloB1);

        // BRAZO2 rota en Z con desfase de fase (π/3) para movimiento más orgánico
        float anguloB2 = Mathf.Sin(t * velocidadB2 + Mathf.PI / 3f) * amplitudB2;
        brazo2.localEulerAngles = new Vector3(0f, 0f, anguloB2);

        // PINZA rota en X (abre/cierra en otro eje)
        float anguloPinza = Mathf.Sin(t * velocidadPinza) * amplitudPinza;
        pinza.localEulerAngles = new Vector3(anguloPinza, 0f, 0f);
    }

    // ─── Trayectoria ──────────────────────────────────────────────
    void RegistrarTrayectoria()
    {
        _puntos[_indice] = extremo.position;
        _indice = (_indice + 1) % maxPuntos;
        if (_indice == 0) _lleno = true;
    }

    void DibujarTrayectoria()
    {
        int total = _lleno ? maxPuntos : _indice;
        if (total < 2) return;

        for (int i = 0; i < total - 1; i++)
        {
            // Índice real en el buffer circular
            int a = (_lleno ? (_indice + i)     % maxPuntos : i);
            int b = (_lleno ? (_indice + i + 1) % maxPuntos : i + 1);

            // Fade: las líneas más viejas son más transparentes
            float alpha = (float)i / (total - 1);
            Color c = new Color(colorLinea.r, colorLinea.g, colorLinea.b, alpha);

            Debug.DrawLine(_puntos[a], _puntos[b], c);
        }
    }
}