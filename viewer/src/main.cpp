#include <SDL2/SDL.h>
#include <iostream>
#include <filesystem>

#include "Decoder.h"

constexpr int WINDOW_WIDTH = 1100;
constexpr int WINDOW_HEIGHT = 780;
constexpr int WINDOW_PADDING = 20;

SDL_Window* window = nullptr;
SDL_Renderer* renderer = nullptr;

void initSdl();
void initWindow();
void initRenderer();
SDL_Surface* createSurfaceFromPixelData(int width, int height, uint32_t* pixelData);
SDL_Texture* createTextureFromSurface(SDL_Surface* surface);
void cleanup();

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Wrong number of arguments. Only valid number is 2" << std::endl;
        return 1;
    }

    std::filesystem::path nyaFilepath(argv[1]);
    
    initSdl();
    initWindow();
    initRenderer();

    NYAImage* image = NYADecoder::decodeFromPath(nyaFilepath);

    if (!image) {
        std::cerr << "Failed to decode NYA image" << std::endl;
        cleanup();
        return 1;
    }

    float widthToHeightRatio = (float) image->width / (float) image->height;
    SDL_Surface* surface = createSurfaceFromPixelData(image->width, image->height, image->pixels);
    SDL_Texture* texture = createTextureFromSurface(surface);

    SDL_FreeSurface(surface);
    delete image;

    SDL_Rect destRect = {0, 0, 0, 0};
    destRect.h = WINDOW_HEIGHT - WINDOW_PADDING;
    destRect.w = destRect.h * widthToHeightRatio;

    if (destRect.w > WINDOW_WIDTH - WINDOW_PADDING) {
        destRect.w = WINDOW_WIDTH - WINDOW_PADDING;
        destRect.h = destRect.w / widthToHeightRatio;
    }

    destRect.x = (WINDOW_WIDTH - destRect.w) / 2;
    destRect.y = (WINDOW_HEIGHT - destRect.h) / 2;

    while(true) {
        SDL_Event event;

        if (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                break;
            }
        }

        SDL_SetRenderDrawColor(renderer, 25, 25, 25, 255);
        SDL_RenderClear(renderer);

        SDL_RenderCopy(renderer, texture, nullptr, &destRect);

        SDL_RenderPresent(renderer);
    }

    SDL_DestroyTexture(texture);
    cleanup();
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

void cleanup() {
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
}