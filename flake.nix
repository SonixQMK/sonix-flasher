{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-21.11";

  outputs = {
    self,
    nixpkgs,
  }: {
    apps = nixpkgs.lib.genAttrs ["x86_64-linux"] (system: {
      default = {
        type = "app";
        program = self.packages.${system}.default + "/bin/sonix-flasher";
      };
    });

    packages = nixpkgs.lib.genAttrs ["x86_64-linux"] (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      default = pkgs.stdenv.mkDerivation {
        name = "sonix-flasher";
        nativeBuildInputs = with pkgs; [makeWrapper];
        buildCommand = ''
          makeWrapper ${self.packages.${system}.env}/bin/fbs $out/bin/sonix-flasher \
            --prefix PATH : ${self.packages.${system}.env}/bin \
            --add-flags run
        '';
      };
      env = pkgs.buildEnv {
        name = "sonix-flasher-env";
        paths = [
          ((pkgs.python39.override {
              packageOverrides = p-self: p-super: let
                buildPyPi = pname: version: propagatedBuildInputs: sha256:
                  with p-super;
                    buildPythonPackage rec {
                      inherit pname version propagatedBuildInputs;
                      doCheck = false;
                      src = fetchPypi {
                        inherit pname version sha256;
                      };
                    };
              in {
                fbs = buildPyPi "fbs" "0.8.6" [p-self.pyinstaller] "sha256-hIGRJlAtlZBQJ8jGp4j5PzGPHADsFk3eXvBtup0ROc8=";
                altgraph = buildPyPi "altgraph" "0.17" [] "sha256-HwWkcSJUL5cCjK94d1oJX75qJpm1CJ3oR361gxZ9aao=";
                macholib = buildPyPi "macholib" "1.14" [p-self.altgraph] "sha256-DENryEfnsdm9oFYDUb9218r5MPtYWoKNE2CIOe9CxDI=";
                pyinstaller = buildPyPi "PyInstaller" "3.4" (with p-self; [altgraph pefile macholib]) "sha256-pabgSmar/Ph2Homi662TeRnGvjOnuJY+GpYbVcs1mGs=";
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
      };
    });
  };
}
