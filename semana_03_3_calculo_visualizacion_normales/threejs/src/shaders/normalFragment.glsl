varying vec3 vNormal;

void main(){

    vec3 color = abs(vNormal);

    gl_FragColor = vec4(color,1.0);

}