import bpy
import os
import csv
import math

# Este arquivo é um modelo para o workshop sobre
# criando planetas no Blender. Ajustar, reescrever e
# estenda as funções de acordo com suas próprias necessidades.

def apagar_planetas():
    """Delete objects with names matching 'Planet-*'"""
    
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="Planet-*")
    n = len(bpy.context.selected_objects)
    bpy.ops.object.delete()

    print("%d planet(s) were deleted." % n)

    return


def apagar_materiais_nao_utilizados():
    """Excluir todos os materiais não utilizados (também feito automaticamente após recarregar)"""
    i = 0
    for mat in bpy.data.materials:
        if mat.users == 0:
            name = mat.name
            bpy.data.materials.remove(mat)
            i = i + 1
            print("Material excluído ", name)

    print("%d materiais foram excluídos." % i)

    return


def apagar_texturas_nao_utilizadas():
    """Excluir todas as texturas não utilizadas"""
    # Tenha cuidado, pois isso realmente exclui todas as texturas que estão atualmente
    # não usado. Ele pode, portanto, excluir mais do que você pretendia.
    i = 0
    for tex in bpy.data.textures:
        if tex.users == 0:
            name = tex.name
            bpy.data.textures.remove(tex)
            i = i + 1
            print("Textura excluída ", name)
            
    print("%d texturas foram deletadas." % i)
    
    return


def adicionar_texturas(mat, imgname):
    """Adicione textura de imagem ao material fornecido, mapeie como esfera
     tapete -- material
     imgname -- nome do arquivo de imagem de textura
    """
    
    # cria textura, adiciona imagem
    img = bpy.data.images.load(imgname)
    tex = bpy.data.textures.new(imgname, type='IMAGE')
    tex.image = img
    
    # adicionar textura ao material, definir mapeamento
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'ORCO'
    mtex.mapping = 'SPHERE' 

    return


def adicionar_material(obj, name):
    """Adicionar material a um objeto
     obj -- objeto ao qual o material é anexado
     name -- basename a ser adicionado ao nome do material
    """
    
    # cria um material
    matname = "Material-" + name
    mat = bpy.data.materials.new(matname)
    mat.diffuse_color = [0,0,1,1] # RGBA
    mat.specular_intensity = 0.1

    # adiciona material ao objeto
    obj.data.materials.append(mat)

    return mat


def adicionar_esfera(name, location):
    """Adicione uma esfera suave à cena atual em um determinado local
     name -- nome para a nova esfera
     location -- localização para a nova esfera
    """
    
    # adicionar objeto
    #bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, size=1.0,location=location, rotation=[0,0,0])
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0,location=location, rotation=[0,0,0])
    
    # pega objeto
    obj = bpy.context.object
    
    # definir nome e sombreamento suave
    obj.name = name
    bpy.ops.object.shade_smooth()
       
    print("Esfera '%s' criada." % name)
   
    return obj
 

if __name__ == '__main__':

    # Determina o diretório atual, usado para poder carregar os arquivos
    dir = os.path.dirname(bpy.data.filepath) + os.sep

    # Apaga os objetos criados préviamente por este script
    apagar_planetas()
    # Apagar texturas de materiais não utilizados
    apagar_materiais_nao_utilizados()
    apagar_texturas_nao_utilizadas()
    
    # Começando.
    
    localizacao = [2.5,0,0]

    nome_planeta = "Terra"
    nome_objeto = "Planet-" + nome_planeta

    # cria planeta como objeto de esfera
    objeto_criado = adicionar_esfera(nome_objeto, localizacao)
    
    # adiciona um material_criadoerial ao objeto
    material_criado = adicionar_material(objeto_criado, nome_planeta)
    
    # Adicionar textura ao material_criadoerial
    nome_imagem = dir + "textures\earth.jpg"
    
    # adicionar_texturas(material_criado, nome_imagem)
    adicionar_texturas(material_criado, nome_imagem)

    # adicionar o achatamento (excentricidade) da esféra planetária
    
    # adicionar inclinação axial 

    # adiciona caminhos de órbita
    
    # adiciona animação de órbita
    
    # adiciona animação de rotação
    
    # adiciona anéis para alguns planetas
        
    # fim do loop
    
