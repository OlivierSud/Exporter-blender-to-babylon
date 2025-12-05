from .abstract import *
from babylon_js.package_level import *

from mathutils import Color

#===============================================================================
class PrincipledBJSNode(AbstractBJSNode):
    bpyType = 'ShaderNodeBsdfPrincipled'

    def __init__(self, bpyNode, socketName, overloadChannels):
        super().__init__(bpyNode, socketName, overloadChannels)

        input = self.findInput('Base Color')
        if input is None:
            input = self.findInput('Base Color') # Try again or fallback? Actually Base Color didn't change.
        # But let's check for other changed inputs

        defaultDiffuse = self.findTexture(input, DIFFUSE_TEX)

        # when defaultDiffuse is None, a texture was found;
        # get color when returned by findTexture, or also when overloading
        if defaultDiffuse is not None or overloadChannels:
            defaultDiffuse = self.getDefault('Base Color')
            self.diffuseColor = Color((defaultDiffuse[0], defaultDiffuse[1], defaultDiffuse[2]))
            self.diffuseAlpha = defaultDiffuse[3]

        self.mustBakeDiffuse = input.mustBake if isinstance(input, AbstractBJSNode) else False
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Subsurface changes in 4.0: Subsurface -> Subsurface Weight
        # Subsurface Color -> Subsurface Radius (Vector) or removed/merged.
        # In 4.0, Subsurface Color is gone. It uses Base Color.
        # But let's check for "Subsurface Weight" first.
        # Subsurface changes in 4.0: Subsurface -> Subsurface Weight
        # Subsurface Color -> Subsurface Radius (Vector) or removed/merged.
        # In 4.0, Subsurface Color is gone. It uses Base Color.
        # But let's check for "Subsurface Weight" first.
        try:
            subsurface = self.getDefault('Subsurface Weight')
        except KeyError:
            try:
                subsurface = self.getDefault('Subsurface')
            except KeyError:
                subsurface = None

        # ignoring texture surfaces & must be greater than 0
        if (subsurface is not None and subsurface > 0):
            # Subsurface Color is tricky in 4.0. It might not exist.
            # If it doesn't exist, we might want to use Base Color or just skip tint.
            # For now, let's try to get it, and if not found, use a default or Base Color.
            try:
                input = self.getDefault('Subsurface Color')
            except:
                input = None

            if input is not None:
                tintColor = Color((input[0], input[1], input[2]))
                self.subSurfaceTintColor = tintColor

            self.subsurfaceTranslucencyIntensity = subsurface
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        input = self.findInput('Metallic')
        defaultMetallic = self.findTexture(input, METAL_TEX)
        if defaultMetallic is not None:
            self.metallic = defaultMetallic

        self.mustBakeMetal = input.mustBake if isinstance(input, AbstractBJSNode) else False
       # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Specular changes in 4.0: Specular -> Specular IOR Level
        input = self.findInput('Specular IOR Level')
        if input is None:
            input = self.findInput('Specular')
        defaultSpecular = self.findTexture(input, SPECULAR_TEX)
        if defaultSpecular is not None:
            self.specularColor = Color((defaultSpecular, defaultSpecular, defaultSpecular))

        self.mustBakeSpecular = input.mustBake if isinstance(input, AbstractBJSNode) else False
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        input = self.findInput('Roughness')
        defaultRoughness = self.findTexture(input, ROUGHNESS_TEX)
        if defaultRoughness is not None:
            self.roughness = defaultRoughness

        self.mustBakeRoughness = input.mustBake if isinstance(input, AbstractBJSNode) else False
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clearcoat changes in 4.0: Clearcoat -> Coat Weight
        input = self.findInput('Coat Weight')
        if input is None:
            input = self.findInput('Clearcoat')
        defaultClearCoatIntensity = self.findTexture(input, CLEARCOAT_TEX)
        self.mustBakeClearCoat = input.mustBake if isinstance(input, AbstractBJSNode) else False

        # Clearcoat Roughness -> Coat Roughness
        input = self.findInput('Coat Roughness')
        if input is None:
            input = self.findInput('Clearcoat Roughness')
        defaultClearCoatRoughness = self.findTexture(input, CLEARCOAT_TEX)
        self.mustBakeClearCoat = input.mustBake if isinstance(input, AbstractBJSNode) else False

        # only want scalars, when no texture on either input & intensity > 0
        if CLEARCOAT_TEX not in self.bjsTextures and defaultClearCoatIntensity is not None and defaultClearCoatIntensity > 0:
            self.clearCoatIntensity = defaultClearCoatIntensity
            self.clearCoatRoughness = defaultClearCoatRoughness
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Sheen changes in 4.0: Sheen -> Sheen Weight
        input = self.findInput('Sheen Weight')
        if input is None:
            input = self.findInput('Sheen')
        defaultSheenIntensity = self.findTexture(input, SHEEN_TEX)
        self.mustBakeSheen = input.mustBake if isinstance(input, AbstractBJSNode) else False

        input = self.findInput('Sheen Tint')
        defaultSheenColor = self.findTexture(input, SHEEN_TEX)
        self.mustBakeSheen = input.mustBake if isinstance(input, AbstractBJSNode) else False

        # only want scalars, when no texture on either input & intensity > 0
        if SHEEN_TEX not in self.bjsTextures and defaultSheenIntensity is not None and defaultSheenIntensity > 0:
            self.sheenIntensity = defaultSheenIntensity
            self.sheenColor = Color((defaultSheenColor, defaultSheenColor, defaultSheenColor))
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Anisotropic changes in 4.0: Anisotropic -> Anisotropy
        try:
            input = self.getDefault('Anisotropy')
        except KeyError:
            try:
                input = self.getDefault('Anisotropic')
            except KeyError:
                input = None

        # ignoring texture surfaces & must be greater than 0
        if (input is not None and input > 0):
            self.anisotropicIntensity = input
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        input = self.findInput('IOR')
        defaultIOR = self.findTexture(input, REFRACTION_TEX)
        if defaultIOR is not None:
            self.indexOfRefraction = defaultIOR

        self.mustBakeRefraction = input.mustBake if isinstance(input, AbstractBJSNode) else False
       # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            self.emissiveIntensity = self.getDefault('Emission Strength')
        except KeyError:
            self.emissiveIntensity = 1.0 # Default if missing

        # Emission changes in 4.0: Emission -> Emission Color
        input = self.findInput('Emission Color')
        if input is None:
            input = self.findInput('Emission')
        defaultEmissive = self.findTexture(input, EMMISIVE_TEX)

        # when defaultEmissive is None, a texture was found;
        # get color when returned by findTexture, or also when overloading
        if defaultEmissive is not None or overloadChannels:
            # Emission changes in 4.0: Emission -> Emission Color
            try:
                defaultEmissive = self.getDefault('Emission Color')
            except:
                defaultEmissive = self.getDefault('Emission')

            self.emissiveColor = Color((defaultEmissive[0], defaultEmissive[1], defaultEmissive[2]))

        self.mustBakeEmissive = input.mustBake if isinstance(input, AbstractBJSNode) else False
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        input = self.findInput('Normal')
        self.findTexture(input, BUMP_TEX)
        self.mustBakeNormal = input.mustBake if isinstance(input, AbstractBJSNode) else False
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Clearcoat Normal -> Coat Normal
        input = self.findInput('Coat Normal')
        if input is None:
            input = self.findInput('Clearcoat Normal')
        self.findTexture(input, CLEARCOAT_BUMP_TEX)
        self.mustBakeNormal = input.mustBake if isinstance(input, AbstractBJSNode) else False
