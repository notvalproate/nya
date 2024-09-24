#include <SDL2/SDL.h>
#include <iostream>

constexpr int WINDOW_WIDTH = 1100;
constexpr int WINDOW_HEIGHT = 780;

SDL_Window* window = nullptr;
SDL_Renderer* renderer = nullptr;

void initSdl();
void initWindow();
void initRenderer();
SDL_Surface* createSurfaceFromPixelData(int width, int height, uint32_t* pixelData);
SDL_Texture* createTextureFromSurface(SDL_Surface* surface);

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

void initSdl() {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cerr << "Error initializing SDL: " << SDL_GetError() << std::endl;
        exit(1);
    }
}

void initWindow() {
    window = SDL_CreateWindow("nyaviewer", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, WINDOW_WIDTH, WINDOW_HEIGHT, SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE);

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

SDL_Surface* createSurfaceFromPixelData(int width, int height, uint32_t* pixelData) {
    SDL_Surface* surface = SDL_CreateRGBSurfaceWithFormatFrom(pixelData, 
                                                              width, height, 
                                                              32, 
                                                              width * sizeof(uint32_t), 
                                                              SDL_PIXELFORMAT_RGBA8888);
    if (!surface) {
        std::cerr << "Failed to create surface: " << SDL_GetError() << std::endl;
        return nullptr;
    }

    return surface;
}

SDL_Texture* createTextureFromSurface(SDL_Surface* surface) {
    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);

    if (!texture) {
        std::cerr << "Failed to create texture: " << SDL_GetError() << std::endl;
        return nullptr;
    }

    return texture;
}