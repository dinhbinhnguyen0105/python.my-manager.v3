import threading, time, sys
from queue import Queue
from typing import Optional, Dict, List
import io, pycurl, json
from urllib.parse import urljoin, urlencode


class RequestViotp:
    def __init__(self, token: str = None):
        self._params = {"token": token}
        self._base_url = "https://api.viotp.com"
        if not token:
            raise ValueError(f"Invalid token: {self._params.get('token')}")

    def get_account_balance(self) -> int:
        try:
            params = self._params.copy()
            url_api = self._RequestViotp__build_api_url("users/balance", params)
            response_data = self._RequestViotp__request(url_api)
            if response_data.get("status_code") != 200:
                raise RequestViotpError(
                    response_data.get("message"),
                    response_data.get("status_code"),
                    response_data,
                )
            data = response_data.get("data", None)
            if data:
                return data.get("balance", None)
            return None
        except RequestViotpError as e:
            raise e

    def list_services(self) -> Dict:
        try:
            params = self._params.copy()
            params.setdefault("country", "vn")
            url_api = self._RequestViotp__build_api_url("service/getv2", params)
            response_data = self._RequestViotp__request(url_api)
            if response_data.get("status_code") != 200:
                raise RequestViotpError(
                    response_data.get("message"),
                    response_data.get("status_code"),
                    response_data,
                )
            data = response_data.get("data", None)
            return data
        except RequestViotpError as e:
            raise e

    def get_service_id(self, service_name: str) -> int:
        list_service = self.list_services()
        if not list_service:
            return -1
        facebook_item = next(
            (
                item
                for item in list_service
                if item.get("name", "").lower() == service_name.lower()
            ),
            None,
        )
        if facebook_item:
            return facebook_item.get("id")
        return -1

    def get_service(self, service_name: str) -> Optional[Dict]:
        try:
            params = self._params.copy()
            service_id = self.get_service_id(service_name=service_name)
            if not service_id:
                raise RequestViotpError(
                    message=f"Could not retrieve service ID for {service_name}"
                )
            params.setdefault("serviceId", service_id)
            url_api = self._RequestViotp__build_api_url("request/getv2", params)
            response_data = self._RequestViotp__request(url_api)
            status_code = response_data.get("status_code")
            message = response_data.get("message")
            if status_code != 200:
                raise RequestViotpError(
                    message=message, error_code=status_code, error_data=response_data
                )
            else:
                data = response_data.get("data")
                return {
                    "phone_number": f"+{data.get('countryCode')}{data.get('phone_number')}",
                    "request_id": data.get("request_id"),
                }
        except RequestViotpError as e:
            print(e)
            return None

    def get_code(self, service_id: int) -> Dict:
        try:
            params = self._params.copy()
            params.setdefault("requestId", service_id)
            url_api = self._RequestViotp__build_api_url("session/getv2", params)
            response_data = self._RequestViotp__request(url_api)
            if response_data.get("status_code") != 200:
                raise RequestViotpError(
                    response_data.get("message"),
                    response_data.get("status_code"),
                    response_data,
                )
            data = response_data.get("data", None)
            status = data.get("Status")
            return {
                "status": status,
                "phone_number": f"+{data.get('CountryCode')}{data.get('Phone')}",
                "code": data.get("Code"),
            }
        except RequestViotpError as e:
            print(e)
            return None

    def _RequestViotp__build_api_url(
        self, endpoint: str, params: Optional[Dict]
    ) -> str:
        full_url = urljoin(self._base_url, endpoint)
        if params:
            return f"{full_url}?{urlencode(params)}"
        return full_url

    def _RequestViotp__request(self, url: str) -> Dict:
        buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.CONNECTTIMEOUT, 60)
        curl.setopt(pycurl.TIMEOUT, 60)
        headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept: application/json, text/plain, */*",
            "Accept-Language: en-US,en;q=0.9",
            "Connection: keep-alive",
        ]
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.perform()
        try:
            code = curl.getinfo(pycurl.RESPONSE_CODE)
            body = buffer.getvalue().decode("utf-8")
            res = json.loads(body)
            if code != 200:
                try:
                    error_message = res.get("message", "Unknown API error")
                    raise Exception(f"API Error {code}: {error_message} (URL: {url})")
                except json.JSONDecodeError:
                    raise Exception(f"HTTP Error {code}: {body} (URL: {url})")
            return res
        except pycurl.error as e:
            raise Exception(f"PycURL Error accessing {url}: {e}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON response from {url}: {body}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while requesting {url}: {e}")
        finally:
            curl.close()


class RequestViotpError(Exception):
    def __init__(
        self, message: str, error_code: Optional[int], error_data: Optional[Dict]
    ):
        super().__init__(message)
        self.error_code = error_code
        self.error_data = error_data

    def __str__(self):
        if self.error_code:
            return f"{self.__class__.__name__} [{self.error_code}]: {self.args[0]}"
        return f"{self.__class__.__name__}: {self.args[0]}"


def get_service_task(api_client: RequestViotp, service_name: str, result_queue: Queue):
    print(
        f"[{threading.current_thread().name}] Starting service info task for {service_name}..."
    )
    service = api_client.get_service(service_name=service_name)
    if service and service.get("request_id"):
        request_id = service.get("request_id")
        phone_number = service.get("phone_number")
        result_queue.put(
            {
                "success": True,
                "service_name": service_name,
                "request_id": request_id,
                "phone_number": phone_number,
            }
        )
    else:
        result_queue.put(
            {
                "success": False,
                "service_name": service_name,
                "request_id": None,
                "phone_number": None,
            }
        )


def get_otp_task(
    api_client: RequestViotp,
    service_name: str,
    request_id: int,
    otp_queue: Queue,
):
    print(
        f"[{threading.current_thread().name}] Starting OTP retrieval for {service_name} (Request ID: {request_id})..."
    )
    if not request_id:
        print(
            f"[{threading.current_thread().name}] Invalid Request ID for {service_name}. Cannot get OTP."
        )
        return
    while True:
        code_info = api_client.get_code(request_id)
        status = code_info.get("status")
        if status:
            if status == 1:
                otp_queue.put(
                    {
                        "code": code_info.get("code"),
                        "phone_number": code_info.get("phone_number"),
                    }
                )
                print(
                    f"[{threading.current_thread().name}] OTP for {service_name}: {code_info.get('code')}"
                )
                break
            elif status == 2:
                print(
                    f"[{threading.current_thread().name}] Phone number {code_info.get('phone_number')} for {service_name} has expired."
                )
                break
            else:
                print(
                    f"[{threading.current_thread().name}] Waiting for OTP for {service_name}..."
                )
                time.sleep(5)
        else:
            print(
                f"[{threading.current_thread().name}] Failed to get code info for {service_name}."
            )
            break


if __name__ == "__main__":
    if len(sys.argv) == 2:
        start_time = time.time()

        api_client = RequestViotp("d655ba7073214b0f95740a511864f1e7")
        service_request_queue = Queue()
        otp_queue = Queue()
        service_threads: List[threading.Thread] = []
        for i in range(int(sys.argv[1])):
            service_thread = threading.Thread(
                target=get_service_task,
                args=(api_client, "facebook", service_request_queue),
                name=f"FacebookServiceThread_{i}",
            )
            service_threads.append(service_thread)
            service_thread.start()

        for service_thread in service_threads:
            service_thread.join()

        otp_threads: List[threading.Thread] = []
        while not service_request_queue.empty():
            item = service_request_queue.get()
            service_name = item.get("service_name")
            if item.get("success"):
                request_id = item.get("request_id")
                phone_number = item.get("phone_number")
                print(phone_number)
                otp_thread = threading.Thread(
                    target=get_otp_task,
                    args=(api_client, service_name, request_id, otp_queue),
                    name=f"FacebookOTPThread_{threading.get_ident()}",
                )
                otp_threads.append(otp_thread)
                otp_thread.start()
            else:
                print(
                    f"[MainThread] Skipping OTP task for {service_name} due to missing Request ID."
                )

        for otp_thread in otp_threads:
            otp_thread.join()

        while not otp_queue.empty():
            item = otp_queue.get()
            print(item)

        end_time = time.time()
        print(f"\nAll tasks completed in {end_time - start_time:.2f} seconds.")

    else:
        print("Usage: python get_phonenumber.py <number_of_threads>")
