#include <SDL2/SDL.h>
#include <iostream>

SDL_Window* window = nullptr;
SDL_Renderer* renderer = nullptr;

void initSdl() {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cerr << "Error initializing SDL: " << SDL_GetError() << std::endl;
        exit(1);
    }
}

void initWindow() {
    window = SDL_CreateWindow("nyaviewer", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 1100, 780, SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE);

    if (window == nullptr) {
        std::cerr << "Error creating window: " << SDL_GetError() << std::endl;
        SDL_Quit();
        exit(1);
    }
}

void initRenderer() {
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

    if (renderer == nullptr) {
        std::cerr << "Error creating renderer: " << SDL_GetError() << std::endl;
        SDL_DestroyWindow(window);
        SDL_Quit();
        exit(1);
    }
}

int main(int argc, char* argv[]) {
    initSdl();
    initWindow();
    initRenderer();

    SDL_Event event;

    while(true) {
        if (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                break;
            }
        }

        SDL_SetRenderDrawColor(renderer, 25, 25, 25, 255);
        SDL_RenderClear(renderer);
        SDL_RenderPresent(renderer);
    }

    SDL_Quit();
    return 0;
}