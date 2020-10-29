""" Credits for the Shader: Martins Upitis
https://www.youtube.com/watch?v=UkskiSza4p0
https://blendswap.com/blend/9572

Component created by Uniday Studio
"""
import bge
import bgl

from mathutils import Vector
from collections import OrderedDict

VERTEX_SHADER = """

attribute vec4 Tangent;
varying vec4 fragPos;
varying vec3 wT, wB, wN; //tangent binormal normal
varying vec3 wPos, pos, viewPos;
//uniform mat4 ModelMatrix;
uniform vec3 cameraPos;
varying float luminance;

mat3 m3( mat4 m )
{
    mat3 result;
    
    result[0][0] = m[0][0]; 
    result[0][1] = m[0][1]; 
    result[0][2] = m[0][2]; 

    result[1][0] = m[1][0]; 
    result[1][1] = m[1][1]; 
    result[1][2] = m[1][2]; 
    
    result[2][0] = m[2][0]; 
    result[2][1] = m[2][1]; 
    result[2][2] = m[2][2]; 
    
    return result;
}

void main() 
{
    /*wPos = vec3(ModelMatrix * gl_Vertex);
    //pos = vec3(gl_Vertex);

    wT   = m3(ModelMatrix)*Tangent.xyz;
    wB   = m3(ModelMatrix)*cross(gl_Normal, Tangent.xyz);
    wN   = m3(ModelMatrix)*gl_Normal;*/

    wPos = vec3(gl_Vertex);
    wT   = Tangent.xyz;
    wB   = cross(gl_Normal, Tangent.xyz);
    wN   = gl_Normal;

    //fragPos = ftransform();
    viewPos = wPos - cameraPos.xyz;
        
    luminance = gl_Color.r;
    gl_Position = ftransform();
}

"""

FRAGMENT_SHADER = """

uniform vec3 sunPos;

uniform sampler2D skySampler;

varying vec4 fragPos; //fragment coordinates
varying vec3 wT, wB, wN; //tangent binormal normal
varying vec3 wPos, pos, viewPos;
uniform vec3 cameraPos;
uniform float bias, lumamount, contrast;
varying float luminance;

vec3 sunDirection = normalize(sunPos);

uniform float turbidity, reileigh;
float reileighCoefficient = reileigh;

const float mieCoefficient = 0.005;
const float mieDirectionalG = 0.80;

vec3 tangentSpace(vec3 v)
{
    vec3 vec;
    vec.xy=v.xy;
    vec.z=sqrt(1.0-dot(vec.xy,vec.xy));;
    vec.xyz= normalize(vec.x*wT+vec.y*wB+vec.z*wN);
    return vec;
}

// constants for atmospheric scattering
const float e = 2.71828182845904523536028747135266249775724709369995957;
const float pi = 3.141592653589793238462643383279502884197169;

const float n = 1.0003; // refractive index of air
const float N = 2.545E25; // number of molecules per unit volume for air at
                        // 288.15K and 1013mb (sea level -45 celsius)
const float pn = 0.035; // depolatization factor for standard air

// wavelength of used primaries, according to preetham
const vec3 lambda = vec3(680E-9, 550E-9, 450E-9);

// mie stuff
// K coefficient for the primaries
const vec3 K = vec3(0.686, 0.678, 0.666);
const float v = 4.0;

// optical length at zenith for molecules
const float rayleighZenithLength = 8.4E3;
const float mieZenithLength = 1.25E3;
const vec3 up = vec3(0.0, 0.0, 1.0);

const float EE = 1000.0;
const float sunAngularDiameterCos = 0.999956676946448443553574619906976478926848692873900859324;

// earth shadow hack
const float cutoffAngle = pi/1.95;
const float steepness = 1.5;


vec3 totalRayleigh(vec3 lambda)
{
    return (8.0 * pow(pi, 3.0) * pow(pow(n, 2.0) - 1.0, 2.0) * (6.0 + 3.0 * pn)) / (3.0 * N * pow(lambda, vec3(4.0)) * (6.0 - 7.0 * pn));
}

float rayleighPhase(float cosTheta)
{    
    return (3.0 / (16.0*pi)) * (1.0 + pow(cosTheta, 2.0));
//  return (1.0 / (3.0*pi)) * (1.0 + pow(cosTheta, 2.0));
//  return (3.0 / 4.0) * (1.0 + pow(cosTheta, 2.0));
}

vec3 totalMie(vec3 lambda, vec3 K, float T)
{
    float c = (0.2 * T ) * 10E-18;
    return 0.434 * c * pi * pow((2.0 * pi) / lambda, vec3(v - 2.0)) * K;
}

float hgPhase(float cosTheta, float g)
{
    return (1.0 / (4.0*pi)) * ((1.0 - pow(g, 2.0)) / pow(1.0 - 2.0*g*cosTheta + pow(g, 2.0), 1.5));
}

float sunIntensity(float zenithAngleCos)
{
    return EE * max(0.0, 1.0 - exp(-((cutoffAngle - acos(zenithAngleCos))/steepness)));
}

float logLuminance(vec3 c)
{
    return log(c.r * 0.2126 + c.g * 0.7152 + c.b * 0.0722);
}


float A = 0.15;
float B = 0.50;
float C = 0.10;
float D = 0.20;
float E = 0.02;
float F = 0.30;
float W = 1000.0;

vec3 Uncharted2Tonemap(vec3 x)
{
   return ((x*(A*x+C*B)+D*E)/(x*(A*x+B)+D*F))-E/F;
}


void main() 
{
    float sunfade = 1.0-clamp(1.0-exp(-(sunPos.z/500.0)),0.0,1.0);
    
    reileighCoefficient = reileighCoefficient - (1.0* (1.0-sunfade));
    
    float sunE = sunIntensity(dot(sunDirection, up));

    // extinction (absorbtion + out scattering)
    // rayleigh coefficients
    vec3 betaR = totalRayleigh(lambda) * reileighCoefficient;

    // mie coefficients
    vec3 betaM = totalMie(lambda, K, turbidity) * mieCoefficient;

    // optical length
    // cutoff angle at 90 to avoid singularity in next formula.
    float zenithAngle = acos(max(0.0, dot(up, normalize(wPos - cameraPos))));
    float sR = rayleighZenithLength / (cos(zenithAngle) + 0.15 * pow(93.885 - ((zenithAngle * 180.0) / pi), -1.253));
    float sM = mieZenithLength / (cos(zenithAngle) + 0.15 * pow(93.885 - ((zenithAngle * 180.0) / pi), -1.253));



    // combined extinction factor   
    vec3 Fex = exp(-(betaR * sR + betaM * sM));

    // in scattering
    float cosTheta = dot(normalize(wPos - cameraPos), sunDirection);

    float rPhase = rayleighPhase(cosTheta*0.5+0.5);
    vec3 betaRTheta = betaR * rPhase;

    float mPhase = hgPhase(cosTheta, mieDirectionalG);
    vec3 betaMTheta = betaM * mPhase;


    vec3 Lin = pow(sunE * ((betaRTheta + betaMTheta) / (betaR + betaM)) * (1.0 - Fex),vec3(1.5));
    Lin *= mix(vec3(1.0),pow(sunE * ((betaRTheta + betaMTheta) / (betaR + betaM)) * Fex,vec3(1.0/2.0)),clamp(pow(1.0-dot(up, sunDirection),5.0),0.0,1.0));

    //nightsky
    vec3 direction = normalize(wPos - cameraPos);
    float theta = acos(direction.y); // elevation --> y-axis, [-pi/2, pi/2]
    float phi = atan(direction.z, direction.x); // azimuth --> x-axis [-pi/2, pi/2]
    vec2 uv = vec2(phi, theta) / vec2(2.0*pi, pi) + vec2(0.5, 0.0);
    //vec3 L0 = texture2D(skySampler, uv).rgb+0.1 * Fex;
    vec3 L0 = vec3(0.1) * Fex;
    
    // composition + solar disc
    //if (cosTheta > sunAngularDiameterCos)
    float sundisk = smoothstep(sunAngularDiameterCos,sunAngularDiameterCos+0.00002,cosTheta);
    //if (normalize(wPos - cameraPos).z>0.0)
    L0 += (sunE * 19000.0 * Fex)*sundisk;


    vec3 whiteScale = 1.0/Uncharted2Tonemap(vec3(W));
    
    vec3 texColor = (Lin+L0);   
    texColor *= 0.04 ;
    texColor += vec3(0.0,0.001,0.0025)*0.3;
    
    float g_fMaxLuminance = 1.0;
    float fLumScaled = 0.1 / luminance;     
    float fLumCompressed = (fLumScaled * (1.0 + (fLumScaled / (g_fMaxLuminance * g_fMaxLuminance)))) / (1.0 + fLumScaled); 

    float ExposureBias = fLumCompressed;
   
    vec3 curr = Uncharted2Tonemap((log2(2.0/pow(luminance,4.0)))*texColor);
    vec3 color = curr*whiteScale;

    vec3 retColor = pow(color,vec3(1.0/(1.2+(1.2*sunfade))));

    
    gl_FragColor.rgb = retColor;
        
    gl_FragColor.a = 1.0;
}
"""

class SkyComponent(bge.types.KX_PythonComponent):
    """
    How to use it: 
        - Create a cube, flip his normals so they will face
    inside and scale it up a lot to cover all your scene.
        - APPLY the Position, Rotation and Scale of the object 
    (Ctrl + A > ...).
        - Add this component to the Cube and type the name of
    your sun lamp to it in the appropriate field.
    
    Enjoy!    
    """
    args = OrderedDict([
        ("Sun Name", "Sun"),
        ("Turbidity", 2.0),
        ("Reileigh", 2.5),        
    ])
    
    def start(self, args):
        self.turbidity = args["Turbidity"]
        self.reileigh  = args["Reileigh"]
        
        self.sun = self.object.scene.objects.get(args["Sun Name"])
        self.camera = self.object.scene.active_camera
        
        self.shader = self.object.meshes[0].materials[0].getShader()
        if self.shader != None:
            if not self.shader.isValid():
                self.shader.setSource(VERTEX_SHADER, FRAGMENT_SHADER, 1)
            self.shader.setAttrib(bge.logic.SHD_TANGENT)
    
    def update(self):
        cPos = self.camera.worldPosition        
        self.shader.setUniform3f('cameraPos', cPos.x, cPos.y, cPos.z)
        
        sPos = self.sun.worldOrientation * Vector([0,0,1])
        self.shader.setUniform3f('sunPos', sPos.x, sPos.y, sPos.z)
        
        self.shader.setUniform1f('turbidity', self.turbidity)
        self.shader.setUniform1f('reileigh', self.reileigh)