{
  description = "Flake to manage python workspace";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    mach-nix.url = "github:DavHau/mach-nix";
  };

  outputs = { self, nixpkgs, flake-utils, mach-nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        python = "python39"; # <--- change here
        pkgs = nixpkgs.legacyPackages.${system};
        # https://github.com/DavHau/mach-nix/issues/153#issuecomment-717690154
        mach-nix-wrapper = import mach-nix { inherit pkgs python; };
        requirements = builtins.readFile ./requirements.txt;
        pythonBuild = mach-nix-wrapper.mkPython { inherit requirements; };
      in {
        devShell = pkgs.mkShell {
          packages = [
            # app packages
            pythonBuild

            pkgs.libkrb5
            pkgs.stdenv.cc
            pkgs.qt5.full
            pkgs.python310Packages.pyqt5
          ];
        };
      });
}
