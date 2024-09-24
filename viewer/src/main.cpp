#include <SDL2/SDL.h>
#include <iostream>

int main(int argc, char* argv[]) {
    SDL_Init(SDL_INIT_VIDEO);

    SDL_Window* window = SDL_CreateWindow("Hello World!", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 800, 600, SDL_WINDOW_SHOWN);

    if (window == nullptr) {
        std::cerr << "Error creating window: " << SDL_GetError() << std::endl;
        return 1;
    }

    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

    if (renderer == nullptr) {
        std::cerr << "Error creating renderer: " << SDL_GetError() << std::endl;
        return 1;
    }

    while(true) {
        SDL_Event event;
        if (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                break;
            }
        }
        
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);
        SDL_RenderPresent(renderer);

    }

    return 0;
}