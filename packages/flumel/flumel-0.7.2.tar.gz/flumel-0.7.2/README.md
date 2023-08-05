# Flumel

[![Intégration continue](https://gitlab.com/canarduck/flumel/badges/master/pipeline.svg)](https://gitlab.com/canarduck/flumel/commits/master) [![Couverture des tests](https://gitlab.com/canarduck/flumel/badges/master/coverage.svg)](https://canarduck.gitlab.io/flumel/) [![Documentation](https://readthedocs.org/projects/flumel/badge/?version=latest)](https://flumel.readthedocs.io/fr/latest/)

Encore un moyen de recevoir ses flux RSS par email

## Principe de fonctionnement

* Une instance publique est accessible sur [flumel.fr](https://flumel.fr), mais on peut également [héberger sa propre version](https://flumel.readthedocs.io/fr/latest/installation) et la personnaliser
* Flumel permet de s’abonner par mail à un flux RSS en envoyant un simple email (par défaut "Abonnement URLDUFLUX") au robot de l'instance.
* Pas de login ni mot de passe ni interface web (enfin si, juste une page statique pour lister les commandes et informer de l’adresse mail du robot).
* Régulièrement (chaque heure sur l’instance publique) les nouveaux articles des flux sont envoyés par email.

Le reste (durée de conservation, tri, classement, mode hors-ligne, etc.) est dans les mains de votre client mail.

Pour plus d’information consulter [la documentation](https://flumel.readthedocs.io/fr/latest/installation)

## Développement

Flumel est activement développé mais n’a pas encore atteint la "version 1.0", le [journal des modifications](https://gitlab.com/canarduck/flumel/blob/master/CHANGELOG.md) permet de suivre l’avancement du projet et le [kanban](https://gitlab.com/canarduck/flumel/boards) liste les tâches à accomplir et bugs à régler.