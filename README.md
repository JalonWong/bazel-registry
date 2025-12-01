# Custom bazel registry

`.bazelrc`:
```shel
common --registry=https://raw.githubusercontent.com/JalonWong/bazel-registry/main/
common --registry=https://raw.githubusercontent.com/bazelbuild/bazel-central-registry/main/
```

`MODULE.bazel`:
```starlark
bazel_dep(name = "rules_arm_clang", version="0.1.0")
```
