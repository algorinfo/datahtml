from datahtml.facebook import FBLink
ex1 = "https://www.facebook.com/story.php?story_fbid=pfbid02G3gFCXMZ5kgXUkoZYFERAztJoaNzJud93tt3cQ8WZ1ghxeEPydfMAsDLGoYTeFkgl&id=100095183804155&mibextid=Nif5oz'"
ex2 = 'https://www.facebook.com/people/Gabriela-Ford-San-Nicol%C3%A1s/100088589533130/'
ex3 = "https://www.facebook.com/grandcarsa/posts/quer%C3%A9s-cumplir-tu-sue%C3%B1o-de-tener-una-jeep-ahora-es-m%C3%A1s-f%C3%A1cil-con-jeep-planrenega/982542428959000"
ex4 = "https://www.facebook.com/burdeosautoplan.larioja"
ex5 = "https://www.facebook.com/profile.php?id=100076743798090"

def test_facebook_parser():
    l1 = FBLink.from_url(ex1)
    l2 = FBLink.from_url(ex2)
    l3 = FBLink.from_url(ex3)
    l4 = FBLink.from_url(ex4)
    l5 = FBLink.from_url(ex5)
    assert l1.is_profile == False
    assert l1.id == "100095183804155"
    assert l1.alias is None
    assert l2.is_profile == True
    assert l2.alias == "Gabriela-Ford-San-Nicol%C3%A1s"
    assert l2.id
    assert l3.is_profile == False 
    assert l3.alias
    assert l4.alias
    assert l4.is_profile
    assert l5.is_profile
    assert l5.id == "100076743798090"
    
