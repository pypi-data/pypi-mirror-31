# git-semver-gen
Generates semver compliant versions based on a specified major/minor version, current branch, and tags that are present. These versions can be used to name artifacts, to populate version numbers in project manifests, etc.

Add a version declaration file (version.json) to your project specifying the current major and minor version:
```
{
  "version": {
    "major": 0,
    "minor": 1
  }
}
```

Use the tool to compute a current version. Using the above version.json file with no previous version tags, we will be working on a prerelease of version 0.1.0. In the example below, you see the generated semver shows this, and that we are on `taskA` branch, and that this is the 6th commit towards this version, and that we are in a dirty state.
```
$ git-semver-gen
0.1.0-taskA.6.8ff14ac-dirty
```

If we commit our change we see the new version...
```
$ git commit -m "save changes"
$ git-semver-gen
0.1.0-taskA.7.17bace8
```

If we pass our tests and merge to master we will get a pre-release on master, but then we can tag for release
```
$ git checkout master
$ git merge taskA
$ git-semver-gen
0.1.0-master.7.2a13dd1
```

Generate a tag to "release" a commit...
```
$ git-semver-gen --tag-string
v0.1.0

$ git tag -a $(git-semver-gen --tag-string) -m 'tag for release'

$ git-semver-gen 
0.1.0
```
