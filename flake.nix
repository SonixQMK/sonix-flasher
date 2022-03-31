{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-21.11";
  };

  outputs = {
    self,
    nixpkgs,
    ...
  }: {
    devShell = nixpkgs.lib.genAttrs ["x86_64-linux"] (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in
      pkgs.mkShell {
        packages = [
          ((pkgs.python39.override {
              packageOverrides = p-self: p-super: {
                fbs = with p-super;
                  buildPythonPackage rec {
                    pname = "fbs";
                    version = "0.8.6";
                    propagatedBuildInputs = [p-self.pyinstaller];
                    doCheck = false;
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-hIGRJlAtlZBQJ8jGp4j5PzGPHADsFk3eXvBtup0ROc8=";
                    };
                  };
                altgraph = with p-super;
                  buildPythonPackage rec {
                    pname = "altgraph";
                    version = "0.17";
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-HwWkcSJUL5cCjK94d1oJX75qJpm1CJ3oR361gxZ9aao=";
                    };
                  };
                macholib = with p-super;
                  buildPythonPackage rec {
                    pname = "macholib";
                    version = "1.14";
                    propagatedBuildInputs = [p-self.altgraph];
                    doCheck = false;
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-DENryEfnsdm9oFYDUb9218r5MPtYWoKNE2CIOe9CxDI=";
                    };
                  };
                pyinstaller = with p-super;
                  buildPythonPackage rec {
                    pname = "PyInstaller";
                    version = "3.4";
                    propagatedBuildInputs = with p-self; [altgraph pefile macholib];
                    doCheck = false;
                    src = fetchPypi {
                      inherit pname version;
                      sha256 = "sha256-pabgSmar/Ph2Homi662TeRnGvjOnuJY+GpYbVcs1mGs=";
                    };
                  };
              };
            })
            .withPackages (p:
              with p; [
                altgraph
                fbs
                future
                hidapi
                macholib
                pefile
                pyinstaller
                pyqt5
                sip
              ]))

          pkgs.libkrb5
          pkgs.stdenv.cc
          pkgs.qt5.full
        ];
      });
  };
}
