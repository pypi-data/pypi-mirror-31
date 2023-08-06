1. Do a release of schemapi if necessary

2. Update version to, e.g. 2.0.0

   - in altair/__init__.py
   - in doc/conf.py (two places)

3. Commit change and push to master

       git add altair -u
       git commit -m "MAINT: bump version to 2.0.0"
       git push origin master

4. Tag the release:

       git tag -a v2.0.0 -m "version 2.0.0 release"
       git push origin v2.0.0

5. publish to PyPI (Requires correct PyPI owner permissions)

       python setup.py sdist upload

6. build and publish docs (Requires write-access to altair-viz/altair-viz.github.io)

       cd docs
       make clean
       make html
       bash sync_website.sh

7. update version to, e.g. 2.1.0dev

   - in altair/__init__.py
   - in doc/conf.py (two places)

8. Commit change and push to master

       git add altair -u
       git commit -m "MAINT: bump version to 2.1.0dev"
       git push origin master

9. Update version and hash in the recipe at conda-forge/altair-feedstock:
   https://github.com/conda-forge/altair-feedstock/blob/master/recipe/meta.yaml
   & submit a pull request

    