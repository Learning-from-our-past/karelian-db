{
  description = "Learniniiig from our Past karelian-db development environment";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.mach-nix.url = "github:DavHau/mach-nix";
  #inputs.mach-nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, flake-utils, mach-nix }:
    flake-utils.lib.eachDefaultSystem (system: let
      python = "python39";
      #pkgs = nixpkgs.legacyPackages.${system}.pkgs;
      pkgs = (import nixpkgs { inherit system; }).pkgs;
      # https://github.com/DavHau/mach-nix/issues/153#issuecomment-717690154
      #mach-nix-wrapper = mach-nix.lib.${system};
      mach-nix-wrapper = import mach-nix { inherit pkgs python; };
      requirements = builtins.readFile ./requirements.txt;
      #pythonBuild = mach-nix.mkPython { inherit requirements; };
      pythonBuild = mach-nix-wrapper.mkPython { inherit requirements; };
    in {
      devShell = pkgs.mkShell {
        buildInputs = [ 
          # dev dependencies 
          (pkgs.${python}.withPackages
            (ps: with ps; [ pip python-lsp-server ]))

          # app dependencies 
          pkgs.postgresql.out
          pkgs.bashInteractive

          #libffi
          #ssdeep
          #zlib

          ##libxml2 <- This is actually a dependency, but it also comes with `libxslt`
          ##           and that package sets up `libxml2` correctly, whereas the actual
          ##           `libxml2` package doesn't 🙄
          #libxslt
          pythonBuild
        ];
        #nativeBuildInputs = [ ];
      };
    });
}
