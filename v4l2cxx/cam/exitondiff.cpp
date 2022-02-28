#include "../src/v4l2cxx.h"

int counter = 0;
uint8_t lastBuff[921600];

void callback_stdout_pipe(uint8_t *p_data, size_t len) {

    uint8_t outBuff[921600];
    util_v4l2::raw_to_rgb(p_data, 0, outBuff, 921600, 640 * 480, 8);
    // fwrite(outBuff, 640*480*3, 1, stdout);
    if (counter % 10 == 0) {
        if (counter > 30) {
            int diff = 0;
            for (int i=0; i<921600; i++) {
                diff += std::abs(outBuff[i] - lastBuff[i]);
            }
            // std::cout << "Avg Diff: " << diff / 921600 << std::endl;
            if ((diff / 921600) > 15) {
                std::exit(0);
            }
        }
        std::copy(std::begin(outBuff), std::end(outBuff), std::begin(lastBuff));
    }
    counter++;
}


int main() {
    
    // std::cout << "Starting Camera..." << std::endl;
    capture cap("/dev/video0", 640,480,pixel_format ::V4L2CXX_PIX_FMT_YUYV,callback_stdout_pipe);
    cap.run();

    }
